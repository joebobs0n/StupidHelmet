#!/usr/bin/env python3

import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

for spot in range(1,35):
    imgL = cv.imread(f'stereo_L{spot}.png')
    imgL = cv.cvtColor(imgL, cv.COLOR_BGR2GRAY)
    imgR = cv.imread(f'stereo_R{spot}.png')
    imgR = cv.cvtColor(imgR, cv.COLOR_BGR2GRAY)
    cv.imshow("pic", imgL)
    cv.waitKey(1)
    disp = 16*4
    blck = 51
    stereo = cv.StereoBM_create(numDisparities=disp, blockSize=blck)
    disparity = stereo.compute(imgL,imgR)
    plt.imshow(disparity,'gray')
    # plt.show()
    plt.draw()
    plt.pause(0.005)
