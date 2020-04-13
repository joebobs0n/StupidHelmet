import numpy as np
import socket


def parseDisparityMap(frame, num_bins, size=(2, 25, 3)):
    # copy out frame data so we don't change it
    temp_frame = frame.copy()
    # initialize return variables
    ret = True
    parsed_frame = np.zeros(size)

    # check to see if frame data provided
    if frame is None:  # if not
        # set return flag to unsuccessful
        ret = False
    else:
        # get frame height (y) and width (x)
        height = temp_frame.shape[0]
        width = temp_frame.shape[1]

        # calculate indices to split frame into desired rows and columns
        x_indices = np.linspace(0, width, size[1]+1)
        y_indices = np.linspace(0, height, size[0]+1)

        # iterate through each partition
        for y in range(size[0]):
            for x in range(size[1]):
                # calculate start and stop x and y indices
                y0 = int(y_indices[y])
                y1 = int(y_indices[y+1])
                x0 = int(x_indices[x])
                x1 = int(x_indices[x+1])
                # pull off frame partition
                partition = frame[y0:y1, x0:x1]
                print("min:", np.min(partition))
                print("max:", np.max(partition))
                # here we can do whatever "statistical analysis" we want
                # for now, i'm just averaging the data
                amounts, lower_bound = np.histogram(partition, np.linspace(0, num_bins/2014, 10))
                result = np.dot(amounts, lower_bound[:-1])
                print(result)
                # partition_data = np.max(partition)
                partition_data = result
                # calculate rgb colors to represent disparity
                rgb = [0, 0, 0]
                if partition_data < 29:  # if nothing detected or very very close
                # if partition_data < 0.046:  # if nothing detected or very very close
                    rgb = [0, 0, 128]  # show blue
                elif partition_data > 270:  # if something detected very far away
                # elif partition_data > 1.8:  # if something detected very far away
                    rgb = [0, 0, 0]  # show black
                else:  # if something detected within 1000 disparity
                    # calculate color mixed from red to green
                    rgb = [partition_data * 128/270,
                           ((270 - partition_data) * 128/270), 0]
                # save rgb value in parsed frame data
                parsed_frame[y, x] = rgb

    # returned frame is [y, x, z] where z is color
    return ret, parsed_frame


class Transmitter():
    # custom class constructor
    def __init__(self, IpAddr='127.0.0.1', UdpPort=12345):
        # intialize socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # set working IP address
        self.SetIP(IpAddr)
        # set working port
        self.SetPort(UdpPort)
        # set transmission data dimensions
        self.SetTransmitDims()

    # method to send data
    def SendData(self, array=None):
        if array is not None:  # if data passed into method
            # transmit desired data
            message = np.float32(array)
        else:  # if no data passed into method
            # transmit random data
            message = np.float32(np.random.randint(
                0, 2, (self.pages, self.rows, 3)) * 255)
        self.s.sendto(message, (self.IP, self.port))

    # method to set working port number
    def SetPort(self, newPort=12345):
        # set port to default '12345' or passed integer
        self.port = int(newPort)

    # method to see current port number
    def GetPort(self):
        # return programmed port number
        return self.port

    # method to set working ip address
    def SetIP(self, newIP='127.0.0.1'):
        # set IP to default '127.0.0.1' or passed address
        self.IP = newIP

    # method to see current IP addres
    def GetIP(self):
        # return programmed IP address
        return self.IP

    # method to set transmit data dimensions
    def SetTransmitDims(self, num_pages=25, num_rows=2):
        # set pages (columns) to default '25' or passed integer
        self.pages = int(num_pages)
        # set rows to default '2' or passed integer
        self.rows = int(num_rows)

    # method to see current transmit data dimensions
    def GetTransmitDims(self):
        # return programmed transmit dimensions data (with included '3' for channel)
        return (self.pages, self.rows, 3)
