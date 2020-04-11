import numpy as np
import socket

# frame returned as y by x to keep with open cv dimension addressing
def parseDisparityMap(frame, size=(2, 25, 3)):
    temp_frame = frame.copy()
    ret = True

    parsed_frame = np.zeros(size))
    # disp_frame = np.zeros(frame.shape)

    height = temp_frame.shape[0]
    h_delta = height/size[0]
    width = temp_frame.shape[1]
    w_delta = width/size[1]

    x_indices = np.linspace(0, width, size[1]+1)
    y_indices = np.linspace(0, height, size[0]+1)

    for y in range(size[0]):
        for x in range(size[1]):
            y0 = int(y_indices[y])
            y1 = int(y_indices[y+1])
            x0 = int(x_indices[x])
            x1 = int(x_indices[x+1])
            partition = frame[y0:y1, x0:x1]
            # here we can do whatever "statistical analysis" we want
            # for now, i'm just averaging the data
            partition_data = np.mean(partition)
            rgb = 
            parsed_frame[y, x] = partition_data

    return ret, parsed_frame#, disp_frame

class Transmitter():
    def __init__(self, IpAddr='127.0.0.1',UdpPort=12345):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.IP = IpAddr
        self.port = UdpPort

    def SendData(self, array=None):
        if array not None:
            message = np.float32(array)
        else:
            message = np.float32(np.random.randint(0,2,(num_pages,num_rows,3))*255)
        self.s.sendto(message, (self.IP, self.port))
