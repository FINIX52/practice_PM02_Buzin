#!/bin/bash
# backup_minio.sh - Резервное копирование MinIO

set -e

MINIO_ALIAS="prod"
BUCKET_NAME="camera-video"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
S3_BUCKET="iot-backups-prod"

# 1. Репликация в другой ЦОД
mc replicate sync ${MINIO_ALIAS}/${BUCKET_NAME} minio-dr/${BUCKET_NAME}

# 2. Создание бэкапа
mc cp ${MINIO_ALIAS}/${BUCKET_NAME} /backup/minio/${TIMESTAMP}/ --recursive

# 3. Сжатие
tar -czf "/backup/minio_${TIMESTAMP}.tar.gz" "/backup/minio/${TIMESTAMP}"

# 4. Загрузка в S3
aws s3 cp "/backup/minio_${TIMESTAMP}.tar.gz" s3://${S3_BUCKET}/minio/${TIMESTAMP}/

echo "MinIO backup completed: ${TIMESTAMP}"