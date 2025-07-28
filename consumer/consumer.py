import os
import yaml
import json
import requests
from utils.logger import get_logger
from confluent_kafka import Consumer

logger = get_logger("consumer")

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
            try:
                data = json.loads(decoded_message)
                logger.info(f"Send data: {data}")
                response = requests.post('http://api:8000/api/meteo', json=data)
                response.raise_for_status()
                logger.info(f"Saved to DB: {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Failed to send request to Meteo: {e}")
            except json.JSONDecodeError:
                logger.error(f"Failed to decode response from Meteo: {decoded_message}")


            #flattened_data = self.__extract_values(data, self.payload['meteo_json_structure'])

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
