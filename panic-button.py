import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)

button = 21

gpio.setup(button, gpio.IN)

while True:
	try:
		if gpio.input(21) == 0:
			print("DETECTED")
			break
	except KeyboardInterrupt:
		print("program complete")
		gpio.cleanup()
		break

