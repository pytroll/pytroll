import os
import re
from datetime import datetime, timedelta
import h5py
import numpy as np
import pyresample as pyr

from npp import get_npp_stamp
from npp.sdr_passage import SDRPassage

try:
    config_dir = os.environ['PPP_CONFIG_DIR']
except KeyError:
    raise IOError("Please define environment variable PPP_CONFIG_DIR")

def get_datatype(h5):
    dt = list(h5['Data_Products'])
    if len(dt) > 1:
        raise IOError("More than one data products in %s"%h5.filename)
    return dt[0]

def is_ascending(h5):
    dt = get_datatype(h5)
    return h5['Data_Products'][dt][dt + '_Gran_0'].\
        attrs['Ascending/Descending_Indicator'][0][0] == 0

def get_lonlats(h5):
    def _first_last_good_line(grid):
        # We expect that a granule can start or end with "bad" lines and if 
        # it's first "bad" it will remain "bad".
        if len(grid.shape) > 1:
            grid = grid[:, 0]
        first, last = -1, -1
        for i, val in enumerate(grid):
            if first < 0 and abs(val) < 361:
                first = i
            elif first >= 0 and abs(val) < 361:
                last = i
        return first, last

    dt = get_datatype(h5)
    lons = h5['All_Data'][dt + '_All']['Longitude'].value
    lats = h5['All_Data'][dt + '_All']['Latitude'].value
    first, last = _first_last_good_line(lons)
    return lons[first:last], lats[first:last]

def get_bounding_box(h5):
    dt = get_datatype(h5)
    geogran = h5['Data_Products'][dt][dt + '_Gran_0']
    return (geogran.attrs['North_Bounding_Coordinate'][0][0],
            geogran.attrs['East_Bounding_Coordinate'][0][0],
            geogran.attrs['South_Bounding_Coordinate'][0][0],
            geogran.attrs['West_Bounding_Coordinate'][0][0])

def get_corners(h5, as_grid=False):
    dt = get_datatype(h5)
    lons, lats = get_lonlats(h5)
    corners = ((lons[0,0], lats[0,0]),
               (lons[0,-1], lats[0,-1]),
               (lons[-1,-1], lats[-1,-1]),
               (lons[-1,0], lats[-1,0]))
    if is_ascending(h5):
        corners = (corners[2], corners[3], corners[0], corners[1])
    if as_grid:
        return (np.array([[corners[0][0], corners[1][0]],
                          [corners[2][0], corners[3][0]]]),
                np.array([[corners[0][1], corners[1][1]],
                          [corners[2][1], corners[3][1]]]))
    else:            
        return corners

def overlaps(filename, area_def):
    with h5py.File(filename, 'r') as h5:
        lons, lats = get_corners(h5, as_grid=True)
        grid = pyr.geometry.GridDefinition(lons, lats)
        if isinstance(area_def, str):
            area_def = pyr.utils.load_area(config_dir + '/areas.def', area_def)
    return grid.overlaps(area_def)

if __name__ == '__main__':
    import sys
    import json
    area = 'krim'
    area_db = config_dir + '/areas.def'
    area_def = pyr.utils.load_area(area_db, area)
    print area_def
    path = os.path.dirname(sys.argv[1])
    stamp = get_npp_stamp(sys.argv[1])
    pas = SDRPassage(stamp.satname, name=area, path=path)
    for f in sys.argv[1:]:
        if overlaps(f, 'krim'):
            pas.append(f)
    if pas.items:
        jsfile = (area + '_' + pas.stamp + '.json')
        pas.dump(jsfile)
