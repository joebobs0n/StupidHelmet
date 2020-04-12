# EXTRA NOTES:
# This book is fantastic.... https://ebookcentral.proquest.com/lib/byu/reader.action?docID=4770094

import numpy as np  # used for calculations and array manipulations
import cv2 as cv  # used for camera interface and robotic vision
import imutils  # used for frame manipulations
# from matplotlib import pyplot as plt
import os  # used to change working directory
import sys  # used to find working path
import stupid_helmet_helpers as stpdhh  # custom supplemental functions/classes

os.chdir(sys.path[0])  # change working directory to script path


# function to close all things and exit script
def quitScript():
    cv.destroyAllWindows()
    cam_l.release()
    cam_r.release()
    exit()


# initialize left and right cameras (comment out video feed or camera feed to disable)
cam_l = cv.VideoCapture('test_footage_left.avi')
cam_r = cv.VideoCapture('test_footage_right.avi')
# cam_l = cv.VideoCapture(3)
# cam_r = cv.VideoCapture(2)

# read in left camera intrinsic and distortion parameters
left_params = np.load('stereo_params/left_params.npz')
mat_l = left_params['mat']
dist_l = left_params['dist']

# read in right camera intrinsic and distortion paramters
right_params = np.load('stereo_params/right_params.npz')
mat_r = right_params['mat']
dist_r = right_params['dist']

# read in stereo rectification paramters
rectify = np.load('stereo_params/rectify_params.npz')
R1 = rectify['R1']
R2 = rectify['R2']
P1 = rectify['P1']
P2 = rectify['P2']

# read in one frame from left and right cameras
ret_l, frame_l = cam_l.read()
ret_r, frame_r = cam_r.read()
# check to see if a frame was received --> if not quit script
if ret_l == False:
    print('Cannot get frame from left camera. Exiting...')
    quitScript()
if ret_r == False:
    print('Cannot get frame from right camera. Exiting...')
    quitScript()
# frame_l = imutils.rotate_bound(frame_l, 90 * 3)  # uncomment if using video feed
# frame_r = imutils.rotate_bound(frame_r, 90 * 1)  # uncomment if using video feed
# save shape of read frames
shape_l = tuple(np.flip(np.shape(frame_l)[0:2]))
shape_r = tuple(np.flip(np.shape(frame_r)[0:2]))
# calculate left and right camera remapping
l1, l2 = cv.initUndistortRectifyMap(
    mat_l, dist_l, R1, P1, shape_l, cv.CV_32FC1)
r1, r2 = cv.initUndistortRectifyMap(
    mat_r, dist_r, R2, P2, shape_r, cv.CV_32FC1)

# create stereo depth map object
stereo = cv.StereoBM_create()


# set parameters
stereo.setBlockSize(21)  # size of disparity block detection
stereo.setMinDisparity(4)  # minimum disparity. Most use 0.
# the range of allowable disparities -> multiples of 16
stereo.setNumDisparities(112)

# stereo.setPreFilterType(1) # 0 = prefilter to a normalized response, 1 is a x sobel filter
# stereo.setPreFilterSize(21) # The block used for the prefilter
# stereo.setPreFilterCap(32) # Saturation applied after prefiltering
# stereo.setTextureThreshold(1) # The amount of texture necessary for a disparity to be determined (otherwise => blank/black)
# stereo.setUniquenessRatio(1) # The amount of uniqueness required for two competing results for a "winner" to be declared

# Maximum size of a dettached blob to be considered as a "speckle"
stereo.setSpeckleWindowSize(10)
# maximum allowable difference between disparities within speckle window
stereo.setSpeckleRange(45)

while True:
    # read out left and right frames
    ret_l, frame_l = cam_l.read()
    ret_r, frame_r = cam_r.read()
    # frame_l = imutils.rotate_bound(frame_l, 90 * 3)  # uncomment if using video feed
    # frame_r = imutils.rotate_bound(frame_r, 90 * 1)  # uncomment if using video feed

    # convert left and right frames to grayscale
    gray_l = cv.cvtColor(frame_l, cv.COLOR_BGR2GRAY)
    gray_r = cv.cvtColor(frame_r, cv.COLOR_BGR2GRAY)

    # exit script if either left or right frame not read
    if ret_l == False or ret_r == False:
        break

    # make left and right frames cononical
    rectify_l = cv.remap(gray_l, l1, l2, cv.INTER_LINEAR)
    rectify_r = cv.remap(gray_r, r1, r2, cv.INTER_LINEAR)

    # stack rectified frames side by side for viewing
    undistort_hstack = np.hstack([rectify_l, rectify_r])
    # show rectified frames
    cv.imshow('stereo frames', undistort_hstack)

    # calculate depth map in terms of disparity
    disparity = stereo.compute(rectify_l, rectify_r)
    # display disparity map
    cv.imshow('preview', disparity/1024)

    # calculate rgb representation to send
    ret, rgb_representation = stpdhh.parseDisparityMap(disparity)
    # calculate viewer and display
    c = 20
    disp_partitioned = np.ones((rgb_representation.shape[0]*c, rgb_representation.shape[1]*c, 3))
    if ret == True:
        for y in range(rgb_representation.shape[0]):
            for x in range(rgb_representation.shape[1]):
                disp_partitioned[y*c:(y+1)*c, x*c:(x+1)*c] = disp_partitioned[y*c:(y+1)*c, x*c:(x+1)*c] * rgb_representation[y][x]
    cv.imshow('led representation', disp_partitioned)

    # wait maximum 1 ms to read keystroke
    k = cv.waitKey(1) & 0xff
    # if escape key read, exit script
    if k == 27:
        break

# close up and quit
quitScript()
