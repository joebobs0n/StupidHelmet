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


while True:
    ret_l, frame_l = cam_l.read()
    ret_r, frame_r = cam_r.read()
    
    gray_l = cv.cvtColor(frame_l, cv.COLOR_BGR2GRAY)
    gray_r = cv.cvtColor(frame_r, cv.COLOR_BGR2GRAY)
    
    if ret_l == False or ret_r == False:
        break
    
    undistort_l = cv.undistort(gray_l, mat_l, dist_l)
    undistort_r = cv.undistort(gray_r, mat_r, dist_r)
    
    disp = 16*4
    block = 51
    
    stereo = cv.StereoBM_create(numDisparities=disp, blockSize=block)
    disparity = stereo.compute(undistort_l, undistort_r)
    
    cv.imshow('preview', disparity)
    
    k = cv.waitKey(1) & 0xff
    if k == 27:
        break
    
cv.destroyAllWindows()
cam_l.release()
cam_r.release()
exit()
