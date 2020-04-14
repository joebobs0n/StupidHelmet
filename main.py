# -------------------------------------------------------------------- IMPORTS --
import numpy as np
import cv2 as cv
import stupid_helmet_helpers as shh
from stupid_helmet_helpers import Transmitter as udptx
import subprocess

# these next three lines are only needed on windows (no effect on linux)
import os
import sys
os.chdir(sys.path[0])  # change working dir to script dir

# ----------------------------------------------------------------- PARAMETERS --
# VARIABLES
index_l = 3  # left camera index
index_r = 2  # right camera index
bm_block = 21  # size of blocks for matching
bm_min = 4  # minimum detectable disparity
bm_n = 7 * 16  # essentially set range
bm_spkl_win = 10  # size of window to detect object edges
bm_spkl_r = 45  # max disparity diff allowed within speckle
led_dims = (2, 25, 3)  # dimensions of led data [y, x, z] where z is RGB
c = 20  # led representation block size (in pixels)
udp_ip =  '192.168.1.223'  #'127.0.0.1'  # udp working network address
udp_port = 12345  # udp port number
frame_counter = 0
frame_send = 2

# FLAGS
showRect_flg = False  # show rectified frames (cononical view)
showDisp_flg = True  # show disparity depth map
showRGB_flg = False  # show led representation

# ------------------------------------------------------------------ FUNCTIONS --
def quitScript():
    cv.destroyAllWindows()  # close all windows created by opencv
    cam_l.release()  # destroy left camera object
    cam_r.release()  # destroy right camera object
    exit()  # exit script

# ------------------------------------------------ GLOBALS AND INITIALIZATIONS --
# INITIALIZE CAMERAS
# print user feedback for left camera
print(f'Initializing left camera at index {index_l}.')
# turn off left camera auto focus
subprocess.Popen(f'v4l2-ctl -d {index_l} -c focus_auto=0', shell=True, stdout=subprocess.PIPE)
# start opencv camera object at left index
cam_l = cv.VideoCapture(index_l)
# change to compressed pixels for faster data transfer
cam_l.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*"MJPG"))
# print user feedback for right camera
print(f'Initializing right camera at index {index_r}.')
# turn off right camera auto focus
subprocess.Popen(f'v4l2-ctl -d {index_r} -c focus_auto=0', shell=True, stdout=subprocess.PIPE)
# start opencv camera object at right index
cam_r = cv.VideoCapture(index_r)
# change to compressed pixels for faster data transfer
cam_r.set(cv.CAP_PROP_FOURCC, cv.VideoWriter_fourcc(*"MJPG"))

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
# check to see both frames were received --> if not quit script
q = False
# check left
if ret_l == False:
    print('Cannot get frame from left camera. Exiting...')
    q = True
# check right
if ret_r == False:
    print('Cannot get frame from right camera. Exiting...')
    q = True
# if either didn't return frame, exit
if q == True:
    quitScript()
# save shape of read frames
shape_l = tuple(np.flip(np.shape(frame_l)[0:2]))
shape_r = tuple(np.flip(np.shape(frame_r)[0:2]))
# calculate left and right camera remapping
l1, l2 = cv.initUndistortRectifyMap(mat_l, dist_l, R1, P1, shape_l, cv.CV_32FC1)
r1, r2 = cv.initUndistortRectifyMap(mat_r, dist_r, R2, P2, shape_r, cv.CV_32FC1)

# INITIALIZE STEREO BLOCK MATCHING OBJECT
# initialize object
sbm = cv.StereoBM_create()
# set parameters for detection
sbm.setBlockSize(bm_block)
sbm.setMinDisparity(bm_min)
sbm.setNumDisparities(bm_n)
sbm.setSpeckleWindowSize(bm_spkl_win)
sbm.setSpeckleRange(bm_spkl_r)

# INITIALIZE UDP TRANSMITTER
tx = udptx(IpAddr=udp_ip, UdpPort=udp_port)

# ------------------------------------------------------------------ MAIN LOOP --
while True:
    # get frame from right and left cameras
    ret_l, frame_l = cam_l.read()
    ret_r, frame_r = cam_r.read()
    # continue only if both frames exist
    if ret_l == True and ret_r == True:
        # FRAME MANIPULATIONS (READ->RECTIFY->CALC DISP->GET RGB)
        # convert frames to grayscale
        gray_l = cv.cvtColor(frame_l, cv.COLOR_BGR2GRAY)
        gray_r = cv.cvtColor(frame_r, cv.COLOR_BGR2GRAY)
        # make left and right frames cononical
        rectify_l = cv.remap(gray_l, l1, l2, cv.INTER_LINEAR)
        rectify_r = cv.remap(gray_r, r1, r2, cv.INTER_LINEAR)
        # calculate depth map in terms of disparity
        dm = sbm.compute(rectify_l, rectify_r)/1024
        dm = dm[:,bm_n:]
        # calculate RGB representation to send to LEDs
        frame_rgb = shh.parseDisparityMap(dm, bm_n, size=led_dims)[1]
        # send the RGB representation to the helmet LEDs
        frame_counter+=1
        if frame_counter%frame_send==0:
            print(frame_counter)
            tx.SendData(frame_rgb)

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
            frame_bgr = np.zeros((led_dims[0]*c, led_dims[1]*c, led_dims[2]))
            # work through each LED data
            for y in range(led_dims[0]):
                for x in range(led_dims[1]):
                    # copy LED color to whole display block within frame
                    frame_bgr[y*c:(y+1)*c-1, x*c:(x+1)*c-1] = np.ones((c-1, c-1, 3)) * np.flip(frame_rgb[y][x])
            # show the frame
            cv.imshow('LED Representation', frame_bgr)

# close up and quit
quitScript()
