#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c20671.ad.smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Code example with OSISAF SST with mpop
"""

from mpop.satellites import PolarFactory
from mpop.imageo import geo_image, palettes
import numpy as np
from datetime import datetime


glbd = PolarFactory.create_scene("Suomi-NPP", "", "viirs",
                                 datetime(2016, 9, 8, 13, 0), "")
glbd.load(['SST'])

areaid = 'euro4'
localdata = glbd.project(areaid)

sstdata = localdata["SST"].sst.data
palette = palettes.sstlut_osisaf_metno()

x = np.ma.where(np.less_equal(sstdata, 0), 0, sstdata - 273.15)

# Convert sst to numbers between 0 and 28, corresponding to the lut:
data = np.ma.where(np.less(x, 0), 28, 28.0 - x)
data = np.ma.where(np.greater(x, 23.0), 4, data)
# And we want discrete values:
data = data.round().astype('uint8')

img = geo_image.GeoImage(data,
                         areaid,
                         glbd.time_slot,
                         fill_value=None,
                         mode="P",
                         palette=palette)
img.save('kurt.png')

#img.add_overlay(color=(220, 220, 220))
# img.show()
# img.save('osisaf_sst_viirs.png')
