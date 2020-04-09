import numpy as np
import cv2 as cv
import imutils
from matplotlib import pyplot as plt
import os
import sys

os.chdir(sys.path[0])

cam_l = cv.VideoCapture('test_footage_left.avi')
cam_r = cv.VideoCapture('test_footage_right.avi')

left_params = np.load('stereo_params/left_params.npz')
right_params = np.load('stereo_params/right_params.npz')

mat_l = left_params['mat']
mat_r = right_params['mat']
dist_l = left_params['dist']
dist_r = right_params['dist']

rectify = np.load('stereo_params/rectify_params.npz')
R1 = rectify['R1']
R2 = rectify['R2']
P1 = rectify['P1']
P2 = rectify['P2']

l1, l2 = cv.initUndistortRectifyMap(mat_l, dist_l, R1, P1, (480, 640), cv.CV_32FC2)
r1, r2 = cv.initUndistortRectifyMap(mat_r, dist_r, R2, P2, (480, 640), cv.CV_32FC2)

while True:
    ret_l, frame_l = cam_l.read()
    ret_r, frame_r = cam_r.read()
    
    gray_l = cv.cvtColor(frame_l, cv.COLOR_BGR2GRAY)
    gray_r = cv.cvtColor(frame_r, cv.COLOR_BGR2GRAY)
    
    if ret_l == False or ret_r == False:
        break
    
    rectify_l = cv.remap(gray_l, l1, l2, cv.INTER_LINEAR)
    rectify_r = cv.remap(gray_r, r1, r2, cv.INTER_LINEAR)
    
    undistort_hstack = np.hstack([rectify_l, rectify_r])
    cv.imshow('stereo frames', undistort_hstack)
    
    # disp = 128
    # block = 21
    
    stereo = cv.StereoBM_create()
    stereo.setMinDisparity(4)
    stereo.setNumDisparities(128)
    stereo.setBlockSize(21)
    stereo.setSpeckleRange(16)
    stereo.setSpeckleWindowSize(45)
    disparity = stereo.compute(rectify_l, rectify_r)
    
    cv.imshow('preview', disparity/1024)
    
    k = cv.waitKey(1) & 0xff
    if k == 27:
        break
    
cv.destroyAllWindows()
cam_l.release()
cam_r.release()
exit()
