import os
import yaml
import json

from confluent_kafka import Consumer

import logging
import sys

# Configura il logger base
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Scrive su stdout → visibile in Docker logs
    ]
)

logger = logging.getLogger(__name__)

class MeteoConsumer:
    def __init__(self,topic,bootstrap_servers, group_id):
        self.payload = self.__load_payload()
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })

        self.consumer.subscribe([topic])



    def consume(self):
        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print('Consumer error: {}'.format(msg.error()))
                continue

            decoded_message = msg.value().decode('utf-8')
            logger.info(f"decoded_message: {decoded_message}")
            logger.info(f"type of decoded_message: {type(decoded_message)}")
            data = json.loads(decoded_message)
            logger.info(f"data: {data}")
            logger.info(f"type of data: {type(data)}")
            flattened_data = self.__extract_values(data, self.payload['meteo_json_structure'])
            logger.info(f"flattened_data: {flattened_data}")
            logger.info(f"type of flattened_data: {type(flattened_data)}")

    @staticmethod
    def __load_payload():
        config_file = os.environ.get("CONFIG_FILE", "config/meteo_payload.yml")
        with open(config_file, "r") as file:
            payload = yaml.safe_load(file)

        return payload

    def __extract_values(self,data,structure):
        result = {}

        for item in structure:
            if isinstance(item, dict):
                for key,subkey in item.items():
                    if key in data:
                        result.update(self.__extract_values(data[key],subkey))
            else:
                if item in data:
                    result[item] = data[item]

        return result

TOPIC = "meteo-topic"
BOOTSTRAP_SERVERS = "kafka:9092"
GROUP_ID = "meteo-group"
meteo_consumer = MeteoConsumer(topic=TOPIC, bootstrap_servers=BOOTSTRAP_SERVERS,group_id=GROUP_ID)
meteo_consumer.consume()
