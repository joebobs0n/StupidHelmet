import cv2 as cv
import numpy as numpy
import imutils
import os
import sys
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('-l', '--left', help='Left camera index')
ap.add_argument('-r', '--right', help='Right camera index')
args = vars(ap.parse_args())

index_l = 0
index_r = 1
if args.get('left'):
	index_l = int(args['left'])
else:
	print('No left index provided')
	exit()
if args.get('right'):
	index_r = int(args['right'])
else:
	print('No right index provided')
	exit()

cam_l = cv.VideoCapture(index_l)
cam_r = cv.VideoCapture(index_r)

ret_l, frame_l = cam_l.read()
ret_r, frame_r = cam_r.read()

if ret_l == False:
	print('No left frame received')
	exit()
if ret_r == False:
	print('No right frame received')
	exit()

# frame_l = imutils.rotate_bound(frame_l, 270)
# frame_r = imutils.rotate_bound(frame_r, 90)

shape_l = (int(frame_l.shape[1]), int(frame_l.shape[0]))
shape_r = (int(frame_r.shape[1]), int(frame_r.shape[0]))

out_l = cv.VideoWriter('new_test_footage_left.avi', cv.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, shape_l)
out_r = cv.VideoWriter('new_test_footage_right.avi', cv.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, shape_r)

while True:
	frame_l = cam_l.read()[1]
	frame_r = cam_r.read()[1]

	if (cv.waitKey(1) & 0xff) == 27:
		break

	out_l.write(frame_l)
	out_r.write(frame_r)

out_l.release()
out_r.release()
cam_l.release()
cam_r.release()
exit()
