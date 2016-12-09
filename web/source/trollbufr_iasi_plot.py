#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Alexander Maul
#
# Author(s):
#
#   Alexander Maul <alexander.maul@dwd.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
        "[%(levelname)s: %(module)s] %(message)s"))
handler.setLevel(logging.WARNING)
logging.getLogger('').setLevel(logging.WARNING)
logging.getLogger('').addHandler(handler)

from trollbufr.bufr import Bufr
from trollbufr import load_file
import numpy as np

TESTFILE = 'TestBulletin_468'
PNGFILE = 'metopa_iasi_ctp_%s.png'
AREA = 'euro'

lon = []
lat = []
pres = []
bfr = Bufr("bufrdc", ".")
for blob, size, header in load_file.next_bufr(TESTFILE):
    bfr.decode(blob)
    print header, bfr.get_meta()['datetime']
    for subset in bfr.next_subset():
        gotit = 0
        for k, m, (v, q) in subset.next_data():
            if gotit:
                continue
            if k == 5001:
                lat.append((0, 0, v))
            if k == 6001:
                lon.append((0, 0, v))
            if k == 7004:
                pres.append((0, 0, v))
                gotit = 1
lons = np.concatenate(lon)
lats = np.concatenate(lat)
pres = np.concatenate(pres) / 100.0 # hPa
pres = np.ma.masked_greater(pres, 1.0e+6)

import pyresample as pr
from pyresample import kd_tree, geometry
from pyresample import utils
swath_def = geometry.SwathDefinition(lons=lons, lats=lats)
area_def = utils.parse_area_file('region_config.cfg', AREA)[0]
result = kd_tree.resample_nearest(swath_def, pres,
                              area_def,
                              radius_of_influence=12000,
                              epsilon=100,
                              fill_value=None)
pr.plot.save_quicklook(PNGFILE % AREA,
                    area_def, result, label='IASI - Cloud Top Pressure',
                    coast_res='l')
