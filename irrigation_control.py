#!/usr/bin/python3

import os
from influxdb import InfluxDBClient
import logging
import time
import schedule


# MIN_MOISTURE_THRESHOLD = 350
# VALVE_DURATION_S = 180
# IRRIGATION_CONTROL_MIN_RATE_H = 1
# IRRIGATION_CONTROL_MAX_RATE_H = 96
# START_WITH_IRRIGATION = True
# DB_UPDATE_INTERVAL_S = 180
MIN_MOISTURE_THRESHOLD = 350
VALVE_DURATION_S = 60
IRRIGATION_CONTROL_MIN_RATE_H = 12
IRRIGATION_CONTROL_MAX_RATE_H = 10
START_WITH_IRRIGATION = False
DB_UPDATE_INTERVAL_S = 180

ML_PER_MIN = 50
N_OUTLETS = 8

client = InfluxDBClient('localhost', 8086, 'admin', 'aY3V2LvFji', 'soil_sensors')
logging.basicConfig(level=logging.NOTSET, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("irrigation_control")

last_irrigation_ts = int(time.time())

def update_irrigation_db(value):
	json_body = [
		{
			"measurement": "irrigation",
			"tags": {
			},
			"fields": {
				"value": value
			}
		}
	]
	client.write_points(json_body)

def update_db_0():
	update_irrigation_db(0)

def get_last_moisture():
	result = client.query('SELECT last(value) FROM moisture')
	return list(result.get_points())[0]['last']

def irrigate(seconds):
	global last_irrigation_ts
	logger.info("Starting irrigation")
	update_irrigation_db(1)
	os.system("./on.sh")
	time.sleep(seconds)
	logger.info("Stopping irrigation")
	update_irrigation_db(1)
	os.system("./off.sh")
	last_irrigation_ts = int(time.time())

def irrigation_control():
	logger.info("Irrigation control")
	moisture = get_last_moisture()
	current_ts = int(time.time())
	logger.info("Last soil moisture: " + str(moisture))
	logger.info("last_irrigation_ts: " + str(last_irrigation_ts))
	if (current_ts - last_irrigation_ts >= IRRIGATION_CONTROL_MAX_RATE_H * 3600):
		logger.info("IRRIGATION_CONTROL_MAX_RATE_H exceeded")
		irrigate(VALVE_DURATION_S)
	if (moisture <= MIN_MOISTURE_THRESHOLD):
		logger.info("MIN_MOISTURE_THRESHOLD exceeded")
		irrigate(VALVE_DURATION_S)


schedule.every(IRRIGATION_CONTROL_MIN_RATE_H).hours.do(irrigation_control)
schedule.every(DB_UPDATE_INTERVAL_S).seconds.do(update_db_0)

if START_WITH_IRRIGATION:
	schedule.run_all()

while True:
	schedule.run_pending()
	time.sleep(1)

