# Copyright (c) 2009, 2011, 2012.
#

# Author(s): 
#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
Reading and calibrating hrpt avhrr data.
Todo:
- AMSU
- Satellites other than noaa19
- Compare output with AAPP 

Calibration:
http://www.ncdc.noaa.gov/oa/pod-guide/ncdc/docs/klm/html/c7/sec7-1.htm

"""
import numpy as np
import numexpr as ne
from datetime import datetime, timedelta
import sys
import os
import struct

def show(data, filename=None):
    """Show the stretched data.
    """
    import Image as pil
    img = pil.fromarray(np.array((data - data.min()) * 255.0 /
                                 (data.max() - data.min()), np.uint8))
    if filename:
        img.save(filename)
    else:
        img.show()

def print_bfield(word):
    """Print the bits of a give word.
    """
    for i in range(10):
        print "bit", i+1, (word & 2**(9 - i))/2**(9 - i)

def bfield(array, bit):
    """return the bit array.
    """
    return (array & 2**(9 - bit + 1)).astype(np.bool)

st_time = datetime.now()

def tic():
    global st_time
    st_time = datetime.now()

def toc():
    print datetime.now() - st_time


def timecode(tc_array):
    word = tc_array[0]
    day = word
    word = tc_array[1]
    msecs = ((127) & word) * 1024
    word = tc_array[2]
    msecs += word & 1023
    msecs *= 1024
    word = tc_array[3]
    msecs += word & 1023
    return datetime(2011, 1, 1) + timedelta(days=int(day/2 - 1),
                                            milliseconds=int(msecs))


## NOAA19
## http://www.ncdc.noaa.gov/oa/pod-guide/ncdc/docs/klm/html/d/app-d.htm

# VIS channels

intersections = np.array([496.43, 500.37, 496.11])
slopes_l = np.array([0.055091, 0.054892, 0.027174])
slopes_h = np.array([0.16253, 0.16325, 0.18798])
intercepts_l = np.array([-2.1415, -2.1288, -1.0881])
intercepts_h = np.array([-55.863, -56.445, -81.491])


# IR channels
d0 = np.array([276.601, 276.683, 276.565, 276.615, 0])
d1 = np.array([0.05090, 0.05101, 0.05117, 0.05103, 0])
d2 = np.array([1.657e-6, 1.482e-6, 1.313e-6, 1.484e-6, 0])
d3 = np.array([0, 0, 0, 0, 0])
d4 = np.array([0, 0, 0, 0, 0])

vc = np.array((2659.7952, 928.1460, 833.2532))
A = np.array((1.698704, 0.436645, 0.253179))
B = np.array((0.996960, 0.998607, 0.999057))

N_S = np.array([0, -5.49, -3.39])

b0 = np.array([0, 5.70, 3.58])
b1 = np.array([0, -0.11187, -0.05991])
b2 = np.array([0, 0.00054668, 0.00024985])


# Constants
               
c1 = 1.1910427e-5 #mW/(m2-sr-cm-4)
c2 = 1.4387752 #cm-K 

def read_u2_bytes(fdes):
    return struct.unpack("<H", fdes.read(2))[0]

## Reading
## http://www.ncdc.noaa.gov/oa/pod-guide/ncdc/docs/klm/html/c4/sec4-1.htm#t413-1

def read_file(filename):
    dtype = np.dtype([('frame_sync', '<u2', (6, )),
                      ('id', [('id', '<u2'),
                              ('spare', '<u2')]),
                      ('timecode', '<u2', (4, )),
                      ('telemetry', [("ramp_calibration", '<u2', (5, )),
                                     ("PRT", '<u2', (3, )),
                                     ("ch3_patch_temp", '<u2'),
                                     ("spare", '<u2'),]),
                      ('back_scan', '<u2', (10, 3)),
                      ('space_data', '<u2', (10, 5)),
                      ('sync', '<u2'),
                      ('TIP_data', '<u2', (520, )),
                      ('spare', '<u2', (127, )),
                      ('image_data', '<u2', (2048, 5)),
                      ('aux_sync', '<u2', (100, ))])

    arr = np.fromfile(filename, dtype=dtype)
    if not np.allclose(np.array((644, 367, 860, 413, 527, 149)),
                       arr["frame_sync"]):
        arr = arr.newbyteorder()
    return arr


## VIS calibration

def vis_cal(vis_data):
    """Calibrates the visual data using dual gain.
    """
    print "Visual calibration"
    vis = np.empty(vis_data.shape, dtype=np.float64)
    for i in range(3):
        ch = vis_data[:, :, i]
        intersect = intersections[i]
        slope_l = slopes_l[i]
        slope_h = slopes_h[i]
        intercept_l = intercepts_l[i]
        intercept_h = intercepts_h[i]

        vis[:, :, i] = ne.evaluate("where(ch > intersect, ch * slope_l + intercept_l, ch * slope_h + intercept_h)")
    return vis

## IR calibration

def ir_cal(ir_data, telemetry, back_scan, space_data):
    alen = array.shape[0]
    print "IR calibration"
    print " Preparing telemetry..."
    factor = np.ceil(alen / 5.0) + 1

    displacement = (telemetry['PRT'][0:5, :] == np.array([0, 0, 0])).sum(1).argmax() + 1
    offset = 4 - (displacement - 1)

    bd0 = np.tile(d0.reshape(-1, 1), (factor, 3))[offset:offset + alen]
    bd1 = np.tile(d1.reshape(-1, 1), (factor, 3))[offset:offset + alen]
    bd2 = np.tile(d2.reshape(-1, 1), (factor, 3))[offset:offset + alen]
    bd3 = np.tile(d3.reshape(-1, 1), (factor, 3))[offset:offset + alen]
    bd4 = np.tile(d4.reshape(-1, 1), (factor, 3))[offset:offset + alen]

    PRT = telemetry['PRT']
    T_PRT = bd0 + PRT * (bd1 + PRT * (bd2 + PRT * (bd3 + PRT * bd4)))

    sublen = np.floor(T_PRT[displacement:, :].shape[0] / 5.0) * 5
    TMP_PRT = T_PRT[displacement:displacement + sublen]

    print " Computing blackbody temperatures..."
    
    MEAN = ((TMP_PRT[::5] +
             TMP_PRT[1::5] +
             TMP_PRT[2::5] +
             TMP_PRT[3::5]) / 4).repeat(5, 0)

    T_BB_beg = np.tile(T_PRT[:displacement].sum(0) / (displacement - 1), (displacement, 1))
    T_BB_end = np.tile(T_PRT[sublen+displacement:].mean(0), (T_PRT.shape[0] - sublen - displacement, 1))

    T_BB = np.vstack([MEAN, T_BB_beg, T_BB_end])
    T_BB_star = A + B * T_BB

    N_BB = (c1 * vc ** 3) / (np.exp((c2 * vc)/(T_BB_star)) - 1)

    C_S = space_data[:,:, 2:].mean(1)
    C_BB = back_scan.mean(1)

    C_E = ir_data[:, :, 2:]

    print " Computing linear part of radiances..."

    C_Sr = C_S.reshape(alen, 1, 3)
    Cr = ((N_BB - N_S) / (C_S - C_BB)).reshape(alen, 1, 3)
    N_lin = ne.evaluate("(N_S + (Cr * (C_Sr - C_E)))")

    print " Computing radiance correction..."
    N_E = ne.evaluate("(b0 + (b2 * N_lin + b1 + 1) * N_lin)")

    print " Computing channels brightness temperatures..."
    T_E_star = ne.evaluate("(c2 * vc / (log(1 + c1 * vc**3 / N_E)))")
    T_E = ne.evaluate("(T_E_star - A) / B")

    return T_E

def scanlines(filename):
    epoch = datetime(2000, 1, 1)
    bytelen = 11090 * 2
    arr = read_file(filename)
    times = ((timecode(tc_array) - epoch) for tc_array in arr["timecode"])
    times = [a.days * 24 * 3600 + a.seconds + (a.microseconds / 1000) / 1000.0 for a in times]
    pos = np.arange(len(times)) * bytelen
    return zip(times, pos, [bytelen] * len(times))

if __name__ == "__main__":
    #f = "/local_disk/data/satellite/hrpt16_NOAA-19_14-APR-2011_03:50:59.801_11235"
    f = sys.argv[1]
    try:
        outfile = sys.argv[2]
    except IndexError:
        outfile = None
    tic = datetime.now()
    array = read_file(f)
    toc = datetime.now()
    print "took", toc - tic, "to read", array["image_data"].shape 
    print "Time of first scanline:", timecode(array["timecode"][0])
    vis = vis_cal(array["image_data"][:, :, :3])
    ir_ = ir_cal(array["image_data"][:, :, 2:], array["telemetry"],
                 array["back_scan"], array["space_data"])

    channels = np.empty(array["image_data"].shape, dtype=np.float64)
    channels[:, :, :2] = vis[:, :, :2]
    channels[:, :, 3:] = ir_[:, :, 1:]
    ch3a = bfield(array["id"]["id"], 10)
    ch3b = np.logical_not(ch3a)
    channels[ch3a, :, 2] = vis[ch3a, :, 2]
    channels[ch3b, :, 2] = ir_[ch3b, :, 0]

    # remove line containing nans...
    to_show = channels[:, :, 1]
    to_show = to_show[~np.isnan(to_show).any(1)]

    # show the result
    show(to_show, filename=outfile)
