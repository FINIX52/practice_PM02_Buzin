# Инструкция по восстановлению — IoT-платформа

## Сценарий 1. Восстановление Kafka + InfluxDB (критические данные)

### Шаг 1. Поднятие инфраструктуры (0–5 мин)
```bash
cd /infra/terraform/backup-region
terraform apply -auto-approve