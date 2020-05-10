#!/usr/bin/python3

import schedule
from influxdb import InfluxDBClient
import logging
import chirp_modbus
import time


SENSOR_NAME = "soil1"
SAMPLING_RATE_S = 5


client = InfluxDBClient('localhost', 8086, 'admin', 'aY3V2LvFji', 'soil_sensors')
sensor = chirp_modbus.SoilMoistureSensor(address=1, serialport='/dev/ttyUSB0')
logging.basicConfig(level=logging.NOTSET, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("sensor_hum_temp.py")


def insert_into_db(temp, moisture):
    json_body = [
        {
            "measurement": "temperature",
            "tags": {
	            "sensor": SENSOR_NAME,
    	    },
            "fields": {
                "value": temp
            }
        },
        {
            "measurement": "moisture",
            "tags": {
	            "sensor": SENSOR_NAME,
    	    },
            "fields": {
                "value": moisture
            }
        }
    ]
    client.write_points(json_body)


def get_sensor_readings():
    moisture = sensor.getMoisture()
    temperature = sensor.getTemperature()
    ts = int(time.time())
    logger.info("Temperature: {} / Moisture: {}".format(temperature, moisture))
    return {"ts": ts, "moisture": moisture, "temperature": temperature}


def query_and_update_db():
	data = get_sensor_readings()
	insert_into_db(data['temperature'], data['moisture'])


schedule.every(SAMPLING_RATE_S).seconds.do(query_and_update_db)


while True:
    schedule.run_pending()
    time.sleep(1)