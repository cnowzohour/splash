#!/usr/bin/python3

import schedule
from influxdb import InfluxDBClient
import logging
import chirp_modbus
import time


SENSOR_NAME = "soil1"
SAMPLING_RATE_S = 60


client = InfluxDBClient('localhost', 8086, 'admin', 'aY3V2LvFji', 'soil_sensors')
sensor = chirp_modbus.SoilMoistureSensor(address=1, serialport='/dev/ttyUSB0')


def insert_into_db(temp, moisture):
    json_body = [
        {
            "measurement": "temperature",
            "tags": {
	            "sensor": sensor_name,
    	    },
            "fields": {
                "value": temp
            }
        },
        {
            "measurement": "moisture",
            "tags": {
	            "sensor": sensor_name,
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
    return {"ts": ts, "moisture": moisture, "temperature": temperature}


def query_and_update_db():
	data = get_sensor_readings()
	insert_into_db(data.temperature, data.moisture)


schedule.every(SAMPLING_RATE_S).seconds.do(query_and_update_db)


while True:
    schedule.run_pending()
    time.sleep(1)