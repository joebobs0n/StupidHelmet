### Michael's stuff he added
import numpy as np
import socket
import matplotlib.pyplot as plt
import matplotlib

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

fig = plt.figure()
ax = fig.add_subplot(111)
x_low = -num_rows/2*100
x_high = num_rows/2*100
y_low = -100
y_high = 100
ax.set_xlim([x_low, x_high])
ax.set_ylim([y_low, y_high])

def cvt_rgb2Hex(rgb):
    return '%02x%02x%02x' % rgb

def plotArray(array):
    rect = []
    num_rows = np.shape(array)[1]
    # print(num_rows)
    for pg, page in enumerate(array):
        # print(pg)
        for rr, row in enumerate(page):
            hex_color = cvt_rgb2Hex((int(row[0]), int(row[1]), int(row[2])))
            rect.append(matplotlib.patches.Rectangle((x_low+100*rr,0-100*pg),100,100,color=f'#{hex_color}'))
            # print(rr+pg*num_rows)
            ax.add_artist(rect[rr+pg*num_rows])
    plt.draw()
    plt.pause(0.001)


while True:
    byte_array, _ = s.recvfrom(buffer_size)
    array = np.frombuffer(byte_array, dtype=np.float32)
    array = np.reshape(array, (num_pages, num_rows, num_cols))
    # print(np.shape(array))
    plotArray(array)
