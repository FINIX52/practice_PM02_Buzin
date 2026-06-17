import subprocess
import boto3
import os
import logging
from datetime import datetime, timedelta
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_NAME = "iot_metadata"
DB_USER = "admin"
S3_BUCKET = "iot-backups-prod"
S3_PREFIX = "postgresql/"
LOCAL_BACKUP_DIR = "/backup/postgresql/"
IMMUTABLE_DAYS = 30

def run_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{LOCAL_BACKUP_DIR}/backup_{timestamp}.dump"
    
    cmd = f"pg_dump -U {DB_USER} -F c -f {backup_file} {DB_NAME}"
    subprocess.run(cmd, shell=True, check=True)
    logger.info(f"Дамп создан: {backup_file}")
    
    compressed = f"{backup_file}.gz"
    subprocess.run(f"gzip -c {backup_file} > {compressed}", shell=True, check=True)
    
    with open(compressed, 'rb') as f:
        checksum = hashlib.sha256(f.read()).hexdigest()
    
    s3 = boto3.client('s3')
    s3_key = f"{S3_PREFIX}{timestamp}/backup.dump.gz"
    with open(compressed, 'rb') as f:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=f,
            ObjectLockMode='GOVERNANCE',
            ObjectLockRetainUntilDate=datetime.now() + timedelta(days=IMMUTABLE_DAYS)
        )
    logger.info(f"Загружен в S3: {s3_key}")
    
    cutoff = datetime.now() - timedelta(days=7)
    for f in os.listdir(LOCAL_BACKUP_DIR):
        fpath = os.path.join(LOCAL_BACKUP_DIR, f)
        if os.path.getctime(fpath) < cutoff.timestamp():
            os.remove(fpath)
            logger.info(f"Удален: {fpath}")

if __name__ == "__main__":
    run_backup()
