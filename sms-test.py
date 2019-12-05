import RPi.GPIO as gpio
from twilio.rest import Client

gpio.setmode(gpio.BCM)
gpio.setup(21, gpio.IN)

account_sid = 'ACa236584f1a676b09632c019e881575db'
auth_token = '2c7c6c1214ecfc2c07adf74b451dec28'
client = Client(account_sid, auth_token)

location = "https://google.com/maps/place/12.8471067,77.6605023"
body = "Panic alarm set off at"+location
while True:
	try:
		if gpio.input(21) == 0:
			print("DETECTED!")
			message = client.messages \
	            .create(
	                 body=body,
	                 from_='+17606215434',
	                 to='+919740254990'
	        )
			print(message.sid)
			print("SENT")
			break

	except KeyboardInterrupt:
		print("program complete")
		gpio.cleanup()
		break
