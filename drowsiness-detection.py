#import modules
from twilio.rest import Client
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
#from playsound import playsound
import argparse
import imutils
import time
import dlib
import cv2
import os
import RPi.GPIO as gpio
from ds_gps import GPS
from ds_sms import sms
gpio.setmode(gpio.BCM)

account_sid = 'ACa236584f1a676b09632c019e881575db'
auth_token = '2c7c6c1214ecfc2c07adf74b451dec28'
client = Client(account_sid, auth_token)

#gpio.setup(24, gpio.OUT)
gpio.setup(21, gpio.IN)
g = GPS()
body = "Panic at https://google.com/maps/place/12.8471067,77.6605023"

def eye_aR(eye):
    # compute the euclidean distances between the two sets of
	# vertical eye landmarks (x, y)-coordinates
	A = dist.euclidean(eye[1], eye[5])
	B = dist.euclidean(eye[2], eye[4])

	# compute the euclidean distance between the horizontal
	# eye landmark (x, y)-coordinates
	C = dist.euclidean(eye[0], eye[3])

	# compute the eye aspect ratio
	ear = (A + B) / (2.0 * C)

	# return the eye aspect ratio
	return ear

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
	help="path to facial landmark predictor")
ap.add_argument("-v", "--video", type=str, default="",
	help="path to input video file")
args = vars(ap.parse_args())

EYE_THRESH = 0.3 #threshold for the eye. if it closes further then it is a blink
EYE_CONSEC_FRAMES = 40 #number of frames the eye should be closed for it to be a blink

COUNTER = 0
TOTAL = 0

print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"] #index for left eye
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

print("[INFO] starting video stream thread...")
#vs = FileVideoStream(args["video"]).start()
#fileStream = True
vs = VideoStream(src=-1).start()
#vs = VideoStream(usePiCamera=True).start()
fileStream = False
#time.sleep(3.0)

while True:
	if fileStream and not vs.more():
		break

	frame = vs.read()
	#time.sleep(3)
	frame = imutils.resize(frame, width=450)
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #grayscale

	rects = detector(gray, 0) #detects the faces

	for rect in rects:
		shape = predictor(gray, rect)
		shape = face_utils.shape_to_np(shape) #converts facial landmarks into np array

		leftEye = shape[lStart:lEnd]
		rightEye = shape[rStart: rEnd]
		leftEAR = eye_aR(leftEye)
		rightEAR = eye_aR(rightEye)
		#average EAR of both eyes
		ear = (leftEAR + rightEAR) / 2.0

		# get convex hull of the eye
		leftEyeHull = cv2.convexHull(leftEye)
		rightEyeHull = cv2.convexHull(rightEye)

		#draw contours around the area of the eye
		cv2.drawContours(frame, [leftEyeHull], -1, (0, 0, 255), 1)
		cv2.drawContours(frame, [rightEyeHull], -1, (0, 0, 255), 1)

		#adds to the counter
		if ear < EYE_THRESH:
			COUNTER += 1
			if COUNTER >= EYE_CONSEC_FRAMES:
				TOTAL += 1
				os.system("aplay beep-02.wav")
				#gpio.output(24, 1)
				#time.sleep(0.0025)
				#gpio.output(24, 0)
				#time.sleep(0.0025)
				cv2.putText(frame, "DROWSINESS DETECTED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

		else:
			COUNTER = 0
#			gpio.output(24, 0)

		cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

	if gpio.input(21) == 0:
		print("DETECTED")
		message = client.messages \
                    .create(
                         body=body,
                         from_='+17606215434',
                         to='+919740254990'
                )
                #print(message.sid)
		print("SENT")

	cv2.imshow('frame', frame)
	key = cv2.waitKey(1) & 0xFF

	if key == ord('q'):
		break

cv2.destroyAllWindows()
vs.stop()
