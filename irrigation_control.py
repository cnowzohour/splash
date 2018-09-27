from gpiozero import LED
from time import sleep
import chirp_modbus

valve = LED(21)
sensor = chirp_modbus.SoilMoistureSensor(address=1, serialport='/dev/ttyUSB0')

while True:
		print("Moisture: " + str(sensor.getMoisture()))
		print("Temperature: " + str(sensor.getTemperature()))
		print("Turning valve on")
		valve.on()
		sleep(5)
		print("Turning valve off")
		valve.off()
		sleep(5)