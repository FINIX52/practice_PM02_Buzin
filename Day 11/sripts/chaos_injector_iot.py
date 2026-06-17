import random
import subprocess
import boto3
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IoTChaosInjector:
    def __init__(self):
        self.s3 = boto3.client('s3')

    def kill_kafka(self):
        logger.warning("[CHAOS] Остановка Kafka...")
        subprocess.run("docker stop kafka-broker", shell=True)

    def corrupt_influxdb(self):
        logger.warning("[CHAOS] Удаление InfluxDB...")
        subprocess.run("docker exec influxdb rm -rf /var/lib/influxdb/data", shell=True)

    def run(self):
        self.kill_kafka()
        self.corrupt_influxdb()
        logger.info("[CHAOS] DR Drill запущен! Восстанавливайте систему.")

if __name__ == "__main__":
    injector = IoTChaosInjector()
    injector.run()
