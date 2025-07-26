import os
import yaml
import time
import json
import logging
import schedule
from confluent_kafka import Producer, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic

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


class MeteoData:
    def __init__(self):
        config_file = os.environ.get("STATION_CONFIG", "config/alp-01.yml")
        with open(config_file, 'r') as f:
            base_data = yaml.safe_load(f)


        self.__station_id = base_data['station_id']
        self.__latitude = base_data['location'].get('latitude')
        self.__longitude = base_data['location'].get('longitude')
        self.__altitude = base_data['location'].get('altitude_m')
        self.interval_seconds = base_data['generation'].get('interval_seconds')
        self.__temperature = base_data['generation'].get('temperature_base')
        self.__humidity = base_data['generation'].get('humidity_base')
        self.__pressure = base_data['generation'].get('pressure_base')
        self.__solar_radiation = base_data['generation'].get('solar_radiation_base')
        self.__wind_speed = base_data['generation'].get('wind_speed_base')
        self.json = None
        self.refresh_data()

    def __generate_dynamic_data(self):
        new_temp = self.__temperature
        new_humidity = self.__humidity
        new_solar_radiation = self.__solar_radiation
        new_wind_speed = self.__wind_speed
        new_pressure = self.__pressure

    def __build_json(self):
        return {
            "timestamp": int(time.time() * 1_000_000),
            "station_id": self.__station_id,
            "location": {
                "latitude": self.__latitude,
                "longitude": self.__longitude,
                "altitude": self.__altitude,
            },
            "wether":{
                "temperature": self.__temperature,
                "humidity": self.__humidity,
                "wind_speed": self.__wind_speed,
                "pressure": self.__pressure,
                "solar_radiation": self.__solar_radiation,
            }
        }

    def refresh_data(self):
        self.__generate_dynamic_data()
        self.json = self.__build_json()


class MeteoProducer:
    def __init__(self, kafka_broker: str, topic_name: str):
        self.kafka_broker = kafka_broker
        self.topic_name = topic_name

        self.admin_client = AdminClient({'bootstrap.servers': self.kafka_broker})

        self._ensure_topic_exists()

        self.producer = Producer({'bootstrap.servers': self.kafka_broker})

    def _ensure_topic_exists(self):
        # Ottieni i topic esistenti
        metadata = self.admin_client.list_topics(timeout=10)
        if self.topic_name in metadata.topics:
            print(f"[INFO] Topic '{self.topic_name}' already exists.")
            return

        # Altrimenti crealo
        new_topic = NewTopic(
            topic=self.topic_name,
            num_partitions=1,
            replication_factor=1,
            config={
                "retention.ms": "3600000",         # 1 ora
                "retention.bytes": "500000000"     # ~500MB
            }
        )

        futures = self.admin_client.create_topics([new_topic])

        for topic, future in futures.items():
            try:
                future.result()
                print(f"[INFO] Topic '{topic}' successfully created.")
            except Exception as e:
                print(f"[ERROR] Failed to create topic '{topic}': {e}")

    def produce_json(self,meteo_data:MeteoData):
        meteo_data.refresh_data()
        def delivery_report(err, msg):
            if err is not None:
                print('Message delivery failed: {}'.format(err))
            else:
                print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

        producer = Producer({'bootstrap.servers': self.kafka_broker})

        #while len(producer) >= 10000:
        producer.poll(0.1)
        logger.info(f"meteo_data.json: {meteo_data.json}")
        logger.info(f"type of meteo_data.json: {type(meteo_data.json)}")
        value = json.dumps(meteo_data.json)
        logger.info(f"value: {value}")
        logger.info(f"type of value: {type(value)}")
        logger.info(f"value.encode('utf-8'): {value.encode('utf-8')}")
        logger.info(f"type of value.encode('utf-8'): {type(value.encode('utf-8'))}")
        producer.produce(self.topic_name, value=value.encode('utf-8'), callback=delivery_report)
        producer.flush()

    def run(self):
        meteo_data = MeteoData()
        interval = meteo_data.interval_seconds
        schedule.every(interval).seconds.do(self.produce_json, meteo_data)

        while True:
            schedule.run_pending()
            time.sleep(1)



KAFKA_BROKER = 'kafka:9092'
TOPIC_NAME = 'meteo-topic'
meteo_producer = MeteoProducer(KAFKA_BROKER, TOPIC_NAME)
meteo_producer.run()

'''def load_station_config():
    config_file = os.environ.get("STATION_CONFIG", "config/alp-01.yml")
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

config = load_station_config()
print(config)
logging.info(f"Producer for: {config['station_id']}")
print(f"Producer for: {config['station_id']}")

start_time = time.time()*1000
generation = config["generation"]


last_send = 0
while True:
    curr_time = int(time.time())
    if curr_time != last_send and curr_time % int(generation['interval_seconds']) == 0:
        last_send = curr_time
        logging.info(f"Producer for: {config['station_id']}")
        #print(f"Producer for: {config['station_id']} - timestamp: {time.time()}")'''

