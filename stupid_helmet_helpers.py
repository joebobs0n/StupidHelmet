import numpy as np

# frame returned as y by x to keep with open cv dimension addressing
def parseDisparityMap(frame, size=(25, 2)):
    temp_frame = frame.copy()
    ret = True
    
    parsed_frame = np.zeros(np.flip(size))
    disp_frame = np.zeros(frame.shape)

    width = temp_frame.shape[1]
    w_delta = width/size[0]
    height = temp_frame.shape[0]
    h_delta = height/size[1]
    
    x_indices = np.linspace(0, width, size[0]+1)
    y_indices = np.linspace(0, height, size[1]+1)

    for y in range(size[1]):
        for x in range(size[0]):
            y0 = int(y_indices[y])
            y1 = int(y_indices[y+1])
            x0 = int(x_indices[x])
            x1 = int(x_indices[x+1])
            partition = frame[y0:y1, x0:x1]
            # here we can do whatever "statistical analysis" we want
            # for now, i'm just averaging the data
            partition_data = np.mean(partition)
            parsed_frame[y, x] = partition_data
    
    return ret, parsed_frame, disp_frame
