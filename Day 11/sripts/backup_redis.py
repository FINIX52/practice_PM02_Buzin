import subprocess
import boto3
import os
import logging
from datetime import datetime, timedelta
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

REDIS_HOST = "localhost"
REDIS_PORT = "6379"
REDIS_PASSWORD = ""
S3_BUCKET = "iot-backups-prod"
S3_PREFIX = "redis/"
LOCAL_BACKUP_DIR = "/backup/redis/"
IMMUTABLE_DAYS = 7
RDB_FILE = "/var/lib/redis/dump.rdb"

def run_backup():
    """Основная функция бэкапа"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        cmd = f"redis-cli -h {REDIS_HOST} -p {REDIS_PORT} BGSAVE"
        if REDIS_PASSWORD:
            cmd = f"redis-cli -h {REDIS_HOST} -p {REDIS_PORT} -a {REDIS_PASSWORD} BGSAVE"
        subprocess.run(cmd, shell=True, check=True)
        logger.info("RDB снимок создан")
        
        backup_file = f"{LOCAL_BACKUP_DIR}/dump_{timestamp}.rdb"
        subprocess.run(f"cp {RDB_FILE} {backup_file}", shell=True, check=True)
        
        compressed = f"{backup_file}.gz"
        subprocess.run(f"gzip -c {backup_file} > {compressed}", shell=True, check=True)
        
        with open(compressed, 'rb') as f:
            checksum = hashlib.sha256(f.read()).hexdigest()
        
        s3 = boto3.client('s3')
        s3_key = f"{S3_PREFIX}{timestamp}/dump.rdb.gz"
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
            "job_name": "redis_backup",
            "status": "success",
            "size_bytes": os.path.getsize(compressed),
            "timestamp": timestamp,
            "checksum_sha256": checksum
        })
        
    except Exception as e:
        logger.error(f"Ошибка бэкапа: {e}")
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
