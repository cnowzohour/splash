import chirp_modbus
from datetime import datetime
import time

SAMPLING_RATE_S = 60

sensor = chirp_modbus.SoilMoistureSensor(address=1, serialport='/dev/ttyUSB0')

fname = datetime.now().strftime("%Y-%m-%d_%H%M%S") + ".csv"
with open(fname, 'w') as f:
    f.write('datetime,ts,moisture,temperature\n')

while True:
		moisture = str(sensor.getMoisture())
		temperature = str(sensor.getTemperature())
		ts = int(time.time())
		dt = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
		with open(fname, 'a') as f:
    		f.write(str(dt) + ',' + str(ts) + ',' + moisture + ',' + temperature + '\n')
		print(datetime.now())
		print("Moisture: " + moisture)
		print("Temperature: " + temperature)
		time.sleep(SAMPLING_RATE_S)
