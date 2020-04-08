import cv2 as cv
import argparse

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--index', help='Camera index')
args = vars(ap.parse_args())

cam_index = 0
if args.get('index'):
	cam_index = int(args['index'])

cam = cv.VideoCapture(cam_index)

while True:
	ret, frame = cam.read()
	if ret == True:
		cv.imshow('view', frame)
	else:
		print('no frame')
		break
	k = cv.waitKey(1) & 0xff
	if k == 27:
		break

cv.destroyAllWindows()
cam.release()
exit()

