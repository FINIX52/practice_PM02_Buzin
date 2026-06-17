import subprocess
import boto3
import os
import logging
from datetime import datetime, timedelta
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INFLUXDB_HOST = "localhost"
INFLUXDB_PORT = "8086"
INFLUXDB_ORG = "iot"
INFLUXDB_BUCKET = "sensor_data"
S3_BUCKET = "iot-backups-prod"
S3_PREFIX = "influxdb/"
LOCAL_BACKUP_DIR = "/backup/influxdb/"
IMMUTABLE_DAYS = 30

def check_disk_space():
    """Проверка свободного места (минимум 20%)"""
    stat = os.statvfs(LOCAL_BACKUP_DIR)
    free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
    if free_gb < 20:
        raise Exception(f"Недостаточно места: {free_gb:.2f} ГБ")
    logger.info(f"Свободно: {free_gb:.2f} ГБ")

def run_backup():
    """Основная функция бэкапа"""
    try:
        check_disk_space()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{LOCAL_BACKUP_DIR}/backup_{timestamp}"
        
        cmd = (
            f"influx backup -host {INFLUXDB_HOST}:{INFLUXDB_PORT} "
            f"-org {INFLUXDB_ORG} -bucket {INFLUXDB_BUCKET} {backup_path}"
        )
        subprocess.run(cmd, shell=True, check=True)
        logger.info(f"Бэкап создан: {backup_path}")
        
        compressed = f"{backup_path}.tar.gz"
        subprocess.run(f"tar -czf {compressed} {backup_path}", shell=True, check=True)
        
        with open(compressed, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        
        s3 = boto3.client('s3')
        s3_key = f"{S3_PREFIX}{timestamp}/backup.tar.gz"
        with open(compressed, 'rb') as f:
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=f,
                ObjectLockMode='GOVERNANCE',
                ObjectLockRetainUntilDate=datetime.now() + timedelta(days=IMMUTABLE_DAYS)
            )
        logger.info(f"Загружен в S3: {s3_key}")
        
        cleanup_local()
        
        send_metric({
            "job_name": "influxdb_backup",
            "status": "success",
            "size_bytes": os.path.getsize(compressed),
            "timestamp": timestamp,
            "checksum_sha256": checksum
        })
        
    except Exception as e:
        logger.error(f"Ошибка бэкапа: {e}")
        send_metric({
            "job_name": "influxdb_backup",
            "status": "failed",
            "error_message": str(e),
            "timestamp": datetime.now().isoformat()
        })
        raise

def cleanup_local(days=7):
    """Удаление локальных файлов старше N дней"""
    cutoff = datetime.now() - timedelta(days=days)
    for f in os.listdir(LOCAL_BACKUP_DIR):
        fpath = os.path.join(LOCAL_BACKUP_DIR, f)
        if os.path.getctime(fpath) < cutoff.timestamp():
            os.remove(fpath)
            logger.info(f"Удален локальный файл: {fpath}")

def send_metric(data):
    """Отправка метрики в мониторинг"""
    import json
    import urllib.request
    try:
        req = urllib.request.Request(
            'http://pushgateway:9091/metrics/job/backup',
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'}
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        logger.warning(f"Не удалось отправить метрику: {e}")

if __name__ == "__main__":
    run_backup()
