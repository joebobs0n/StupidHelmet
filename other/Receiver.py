# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
import time
### Michael's stuff he added
import numpy as np
import socket
host = '127.0.0.1'
port = 12345
buffer_size = 1024
num_pages = 2
num_rows = 25
num_cols = 3

# configure udp socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind((host, port))
### End of Michael's stuff (for this section)

from neopixel import *

# LED strip configuration:
LED_1_COUNT      = num_rows      # Number of LED pixels.
LED_1_PIN        = 18      # GPIO pin connected to the pixels (must support PWM! GPIO 13 and 18 on RPi 3).
LED_1_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_1_DMA        = 10      # DMA channel to use for generating signal (Between 1 and 14)
LED_1_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest
LED_1_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_1_CHANNEL    = 0       # 0 or 1
LED_1_STRIP      = ws.WS2811_STRIP_GRB

LED_2_COUNT      = num_rows      # Number of LED pixels.
LED_2_PIN        = 13      # GPIO pin connected to the pixels (must support PWM! GPIO 13 or 18 on RPi 3).
LED_2_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_2_DMA        = 11      # DMA channel to use for generating signal (Between 1 and 14)
LED_2_BRIGHTNESS = 128     # Set to 0 for darkest and 255 for brightest
LED_2_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_2_CHANNEL    = 1       # 0 or 1
LED_2_STRIP      = ws.WS2811_STRIP_GRB


def blackout(strip):
    for i in range(max(strip1.numPixels(),strip1.numPixels())):
        strip.setPixelColor(i, Color(0,0,0))
        strip.show()

def colorArray(strip,array):
    for rr, row in enumerate(array):
#        print("row:", row)
        strip.setPixelColor(rr, Color(int(row[0]), int(row[1]), int(row[2])))
        strip.show()

# Main program logic follows:
if __name__ == '__main__':
    # Create NeoPixel objects with appropriate configuration for each strip.
    strip1 = Adafruit_NeoPixel(LED_1_COUNT, LED_1_PIN, LED_1_FREQ_HZ, LED_1_DMA, LED_1_INVERT, LED_1_BRIGHTNESS, LED_1_CHANNEL, LED_1_STRIP)
    strip2 = Adafruit_NeoPixel(LED_2_COUNT, LED_2_PIN, LED_2_FREQ_HZ, LED_2_DMA, LED_2_INVERT, LED_2_BRIGHTNESS, LED_2_CHANNEL, LED_2_STRIP)
    #Intialize the library (must be called once before other functions).
    strip1.begin()
    strip2.begin()
    print ('Press Ctrl-C to quit.')
    # Black out any LEDs that may be still on for the last run
    blackout(strip1)
    blackout(strip2)

    while True:
        byte_array, _ = s.recvfrom(buffer_size)
        array = np.frombuffer(byte_array, dtype=np.float32)
        array = np.reshape(array, (num_pages, num_rows, num_cols))
        colorArray(strip1,array[0])
        colorArray(strip2,array[1])
