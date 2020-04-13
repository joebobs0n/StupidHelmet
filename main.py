# -------------------------------------------------------------------- IMPORTS --
import numpy as np
import cv2 as cv
import stupid_helmet_helpers as shh
from stupid_helmet_helpers import Transmitter as tx
import argparse

# these next three lines are only needed on windows
import os
import sys
os.chdir(sys.path[0])  # change working dir to script dir

# ----------------------------------------------------------------- PARAMETERS --
# VARIABLES
index_l = 3  # left camera index
index_r = 2  # right camera index
bm_block = 21  # size of blocks for matching
bm_min = 4  # minimum detectable disparity
bm_n = 7  # essentially set range (mutiplied by 16 below)
bm_spkl_win = 10  # size of window to detect object edges
bm_spkl_r = 45  # max disparity diff allowed within speckle
led_dims = (2, 25, 3)  # dimensions of led data [y, x, z] where z is RGB
c = 20  # led representation block size (in pixels)

# FLAGS
showRect_flg = True
showDisp_flg = True
showRGB_flg = True

# ------------------------------------------------------------------ FUNCTIONS --
def quitScript():
    cv.destroyAllWindows()
    cam_l.release()
    cam_r.release()
    exit()

# ------------------------------------------------ GLOBALS AND INITIALIZATIONS --
# INITIALIZE CAMERAS
cam_l = cv.VideoCapture(index_l)  # change for current left index
cam_r = cv.VideoCapture(index_r)  # change for current right index

# SETUP VARIABLES FOR STEREO RECTIFICATION
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
frame_l = cv.rotate(frame_l, cv.ROTATE_90_COUNTERCLOCKWISE)
frame_r = cv.rotate(frame_r, cv.ROTATE_90_CLOCKWISE)
# save shape of read frames
shape_l = tuple(np.flip(np.shape(frame_l)[0:2]))
shape_r = tuple(np.flip(np.shape(frame_r)[0:2]))
# calculate left and right camera remapping
l1, l2 = cv.initUndistortRectifyMap(
    mat_l, dist_l, R1, P1, shape_l, cv.CV_32FC1)
r1, r2 = cv.initUndistortRectifyMap(
    mat_r, dist_r, R2, P2, shape_r, cv.CV_32FC1)

# INITIALIZE STEREO BLOCK MATCHING OBJECT
# initialize object
sbm = cv.StereoBM_create()
# set parameters for detection
sbm.setBlockSize(bm_block)
sbm.setMinDisparity(bm_min)
sbm.setNumDisparities(bm_n * 16)
sbm.setSpeckleWindowSize(bm_spkl_win)
sbm.setSpeckleRange(bm_spkl_r)

# ------------------------------------------------------------------ MAIN LOOP --
while True:
    # get frame from right and left cameras
    ret_l, frame_l = cam_l.read()
    ret_r, frame_r = cam_r.read()
    # continue only if both frames exist
    if ret_l == True and ret_r == True:
        # FRAME MANIPULATIONS (READ->RECTIFY->CALC DISP->GET RGB)
        # rotate frames appropriately
        frame_l = cv.rotate(frame_l, cv.ROTATE_90_COUNTERCLOCKWISE)
        frame_r = cv.rotate(frame_r, cv.ROTATE_90_CLOCKWISE)
        # convert frames to grayscale
        gray_l = cv.cvtColor(frame_l, cv.COLOR_BGR2GRAY)
        gray_r = cv.cvtColor(frame_r, cv.COLOR_BGR2GRAY)
        # make left and right frames cononical
        rectify_l = cv.remap(gray_l, l1, l2, cv.INTER_LINEAR)
        rectify_r = cv.remap(gray_r, r1, r2, cv.INTER_LINEAR)
        # calculate depth map in terms of disparity
        dm = sbm.compute(rectify_l, rectify_r)
        # calculate RGB representation to send to LEDs
        frame_rgb = shh.parseDisparityMap(dm, size=led_dims)[1]

        # GET USER INPUT (IF NECESSARY)
        # wait maximum 1 ms to read keystroke
        k = cv.waitKey(1) & 0xff
        # if escape key read, exit script
        if k == 27:
            break

        # LOCAL VISUAL FEEDBACK (IF FLAGS SET)
        # show rectified frames
        if showRect_flg == True:
            # stack the frame side by side
            frame_rect = np.hstack([rectify_l, rectify_r])
            # show the frame
            cv.imshow('Rectified Stereo Inputs', frame_rect)
        # show depth map
        if showDisp_flg == True:
            # show the depth map
            cv.imshow('Depth Map (disparity)', dm)
        # show RGB output
        if showRGB_flg == True:
            # initialize frame
            frame_bgr = np.ones((led_dims[0]*c, led_dims[1]*c, led_dims[2]))
            # work through each LED data
            for y in range(led_dims[0]):
                for x in range(led_dims[1]):
                    # copy LED color to whole display block within frame
                    frame_bgr[y*c:(y+1)*c, x*c:(x+1)*c] = frame_bgr[y*c:(y+1)*c, x*c:(x+1)*c] * np.flip(frame_rgb[y][x])
            # show the frame
            cv.imshow('LED Representation', frame_bgr)

# close up and quit
quitScript()
