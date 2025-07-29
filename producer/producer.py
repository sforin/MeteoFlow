import os
import yaml
import time
import json
import schedule
import pandas as pd
import random
from scipy.interpolate import griddata
from datetime import datetime
import numpy as np
from confluent_kafka import Producer, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
from state.utils import get_recent_data, save_new_entry
from utils.logger import get_logger

logger = get_logger("producer")


class MeteoData:
    def __init__(self):
        config_file = os.environ.get("STATION_CONFIG", "config/alp-01.yml")
        with open(config_file, 'r') as f:
            base_data = yaml.safe_load(f)

        self.__timestamp = int(time.time() * 1_000_000)
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

    def __get_seasonal_temperature(self):
        current_altitude = self.__altitude
        current_time = datetime.now()
        temp_data = pd.read_csv("data/temperature.csv",sep=";")
        temp_data["altitude"] = temp_data["altitude"].astype(int)
        temp_data["hour"] = temp_data["hour"].astype(int)

        month = current_time.month
        hour = current_time.hour

        hour_points = np.arange(0, 24, 4)
        before_hour = hour_points[hour_points <= hour].max()
        after_hour = hour_points[hour_points >= hour].min() if hour < 20 else 0

        df = temp_data[temp_data["month"] == month]
        df_before = df[df["hour"] == before_hour]
        df_after = df[df["hour"] == after_hour]
        logger.info(f"current altitude: {current_altitude}")
        logger.info(f"df_before[altitude]: {len(df_before["altitude"])}")
        logger.info(f"df_before[temperature]: {len(df_before["temperature"])}")
        temp_before = np.interp(current_altitude, df_before["altitude"], df_before["temperature"])
        temp_after = np.interp(current_altitude, df_after["altitude"], df_after["temperature"])

        weight = (hour - before_hour) / 4 if before_hour != after_hour else 0
        seasonal_temp = (1 - weight) * temp_before + weight * temp_after

        return seasonal_temp

    def __generate_temperature(self):
        seasonal_temp = self.__get_seasonal_temperature()
        history = get_recent_data(self.__station_id)
        if not history:
            return seasonal_temp + random.uniform(-2, 2)

        last_temp = history[0].temperature
        variation = random.uniform(-0.5, 0.5)
        return round(last_temp + variation, 1)

    def __generate_meteo_data(self):
        self.__temperature = self.__generate_temperature()
        self.__humidity = random.uniform(60, 80)
        self.__wind_speed = random.uniform(1, 5)
        self.__pressure = 890 + random.uniform(-2, 2)
        self.__solar_radiation = random.uniform(100, 300)

        data = {
            "timestamp": self.__timestamp,
            "station_id": self.__station_id,
            "temperature": self.__temperature,
            "humidity": self.__humidity,
            "wind_speed": self.__wind_speed,
            "pressure": self.__pressure,
            "solar_radiation": self.__solar_radiation
        }

        save_new_entry(data)
        return data



    def __build_json(self):
        return {
            "timestamp": int(time.time() * 1_000_000),
            "station_id": self.__station_id,
            "location": {
                "latitude": self.__latitude,
                "longitude": self.__longitude,
                "altitude": self.__altitude,
            },
            "weather":{
                "temperature": self.__temperature,
                "humidity": self.__humidity,
                "wind_speed": self.__wind_speed,
                "pressure": self.__pressure,
                "solar_radiation": self.__solar_radiation,
            }
        }

    def refresh_data(self):
        self.__generate_meteo_data()
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

