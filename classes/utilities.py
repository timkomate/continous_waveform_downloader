import numpy as np
import math


def downweight_ends(data, wlength):
    w = (1 - np.cos((math.pi / wlength) * (np.arange(0,wlength,1) + 1)))/2
    data[0:int(wlength)] = data[0:int(wlength)]*w
    w = np.flipud(w)
    data[-int(wlength):] = data[-int(wlength):]*w
    return data