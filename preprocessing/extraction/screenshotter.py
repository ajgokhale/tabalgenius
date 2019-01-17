# Given a video, set of timestamps and burst size, 
# take burst screenshot of video

import cv2
import peaks

FRAMERATE = 30		# video framerate
TEST_FILE = "../../data/raw-videos/IMG_9512.wav"
VIDEO_FILE = "../../../cs231n/data/IMG_9512.MOV"

def screenshotter(timestamps, burst_size=1, output_filepath='./'):
	frames = [timestamp * FRAMERATE for timestamp in timestamps]
	cap = cv2.VideoCapture(VIDEO_FILE)
	
	# get frame and snap img
	for index in range(len(frames)):
		frame = frames[index]
		print(frame)
		cap.set(1, frame)
		_, img = cap.read()
		cv2.imwrite(output_filepath + str(index) + '.png', img)

		# burst
		if index == 0:
			for i in range(burst):
				cap.set(1, frame + i)
				_, img = cap.read()
				cv2.imwrite(output_filepath + str(index) + "_" + str(i) + '.png', img)

		else:
			# burst by saving previous 5 as well
			for i in range(burst):
				cap.set(1, frame - i)
				_, img = cap.read()
				cv2.imwrite(output_filepath + str(index) + "_" + str(i) + '.png', img)

 
 ### FOR TESTING ###

timestamps = peaks.find_peaks(TEST_FILE)
screenshotter(timestamps)