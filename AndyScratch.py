import numpy as np
import cv2 as cv
import imutils
from matplotlib import pyplot as plt
import os
import sys
import stupid_helmet_helpers as stpdhh

os.chdir(sys.path[0])

cam_l = cv.VideoCapture('test_footage_left.avi')
cam_r = cv.VideoCapture('test_footage_right.avi')
# cam_l = cv.VideoCapture(3)
# cam_r = cv.VideoCapture(2)

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

l1, l2 = cv.initUndistortRectifyMap(mat_l, dist_l, R1, P1, (480, 640), cv.CV_32FC1)
r1, r2 = cv.initUndistortRectifyMap(mat_r, dist_r, R2, P2, (480, 640), cv.CV_32FC1)

stereo = cv.StereoBM_create()

# This book is fantastic.... https://ebookcentral.proquest.com/lib/byu/reader.action?docID=4770094

stereo.setBlockSize(21)

stereo.setMinDisparity(4)# # minimum disparity. Most use 0.
stereo.setNumDisparities(112)#176 # the range of allowable disparities

# stereo.setPreFilterType(1) # 0 = prefilter to a normalized response, 1 is a x sobel filter
# stereo.setPreFilterSize(21) # The block used for the prefilter
# stereo.setPreFilterCap(32) # Saturation applied after prefiltering
#
# stereo.setTextureThreshold(1) # The amount of texture necessary for a disparity to be determined (otherwise => blank/black)
#
# stereo.setUniquenessRatio(1) # The amount of uniqueness required for two competing results for a "winner" to be declared

stereo.setSpeckleWindowSize(10)#45 # Maximum size of a dettached blob to be considered as a "speckle"
stereo.setSpeckleRange(45)#16 # Maximum allowable difference between pixels in a speckle. Otherwise flood-fill?

while True:
    ret_l, frame_l = cam_l.read()
    ret_r, frame_r = cam_r.read()
    # frame_l = imutils.rotate_bound(frame_l, 90 * 3)
    # frame_r = imutils.rotate_bound(frame_r, 90 * 1)


    gray_l = cv.cvtColor(frame_l, cv.COLOR_BGR2GRAY)
    # gray_l = np.flip(np.shape(gray_l))
    gray_r = cv.cvtColor(frame_r, cv.COLOR_BGR2GRAY)

    if ret_l == False or ret_r == False:
        break

    rectify_l = cv.remap(gray_l, l1, l2, cv.INTER_LINEAR)
    rectify_r = cv.remap(gray_r, r1, r2, cv.INTER_LINEAR)

    undistort_hstack = np.hstack([rectify_l, rectify_r])
    cv.imshow('stereo frames', undistort_hstack)

    disparity = stereo.compute(rectify_l, rectify_r)

    # ret, disp_partitioned, disp_frame = stpdhh.parseDisparityMap(disparity, size=(2, 25, 3))
    ret, disp_partitioned = stpdhh.parseDisparityMap(disparity, size=(2, 25, 3))
    if ret == True:
        print(disp_partitioned)

    cv.imshow('preview', disparity/1024)

    k = cv.waitKey(1) & 0xff
    if k == 27:
        break

cv.destroyAllWindows()
cam_l.release()
cam_r.release()
exit()
