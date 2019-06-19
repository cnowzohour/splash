from gpiozero import LED
import chirp_modbus
from datetime import datetime
import time
import schedule


SAMPLING_RATE_S = 60
IRRIGATION_CONTROL_MIN_RATE_H = 6
# IRRIGATION_CONTROL_MIN_RATE_H = 0.1
IRRIGATION_CONTROL_MAX_RATE_H = 48
MIN_MOISTURE_THRESHOLD = 270
VALVE_DURATION_S = 60
WET_MODE = True
ML_PER_S = 50.0 / 120.0
START_WITH_IRRIGATION = False


last_irrigation_ts = int(time.time())


def get_sensor_readings():
    moisture = sensor.getMoisture()
    temperature = sensor.getTemperature()
    ts = int(time.time())
    return {"ts": ts, "moisture": moisture, "temperature": temperature}

def ts_to_timestr(ts):
    return str(datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))

def write_line(line, fname):
    with open(fname, 'a') as f:
        f.write(line + '\n')

def write_sensor_readings():
    readings = get_sensor_readings()
    print(readings)
    write_line(
      ts_to_timestr(readings['ts']) + ',' + str(readings['ts']) + ',' + str(readings['moisture']) + ',' + str(readings['temperature']) + '\n',
      fname_readings
    )

def log(msg):
    line = ts_to_timestr(int(time.time())) + " " + msg
    print(line)
    write_line(line, fname_log)

def irrigate(duration_s):
    global last_irrigation_ts
    log("Turning valve on")
    if WET_MODE:
        valve.on()
    time.sleep(duration_s)
    if WET_MODE:
        valve.off()
    log("Turning valve off")
    last_irrigation_ts = int(time.time())

def irrigation_control():
    log("Irrigation control")
    readings = get_sensor_readings()
    log("Sensor readings: " + str(readings))
    log("last_irrigation_ts: " + str(last_irrigation_ts))
    if (readings['ts'] - last_irrigation_ts >= IRRIGATION_CONTROL_MAX_RATE_H * 3600):
        log("IRRIGATION_CONTROL_MAX_RATE_H exceeded")
        irrigate(VALVE_DURATION_S)
    if (readings['moisture'] <= MIN_MOISTURE_THRESHOLD):
        log("MIN_MOISTURE_THRESHOLD exceeded")
        irrigate(VALVE_DURATION_S)


schedule.every(SAMPLING_RATE_S).seconds.do(write_sensor_readings)
schedule.every(IRRIGATION_CONTROL_MIN_RATE_H).hours.do(irrigation_control)


valve = LED(21)
sensor = chirp_modbus.SoilMoistureSensor(address=1, serialport='/dev/ttyUSB0')


date_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
fname_readings = date_str + ".csv"
with open(fname_readings, 'w') as f:
    f.write('datetime,ts,moisture,temperature\n')
fname_log = date_str + ".log"
with open(fname_log, 'w') as f:
    f.write('Log\n')


if START_WITH_IRRIGATION:
    schedule.run_all()


while True:
    schedule.run_pending()
    time.sleep(1)
