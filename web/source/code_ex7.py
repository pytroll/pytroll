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

"""Code example with OSISAF SST with satpy

"""

from satpy.scene import Scene
#from satpy.utils import debug_on
# debug_on()

if __name__ == '__main__':

    scn = Scene(
        sensor='viirs',
        satid='NPP',
        filenames=[
            "/home/a000680/data/osisaf/S-OSI_-FRA_-NPP_-NARSST_FIELD-201609081300Z.nc"],
        reader='ghrsst_osisaf'
    )

    scn.load(['sea_surface_temperature'])
    lcd = scn.resample('euro4', radius_of_influence=2000)

    sstdata = lcd['sea_surface_temperature'][:]
    import numpy as np
    arr = np.ma.where(np.less_equal(sstdata, 0), 0, sstdata - 273.15)

    # Convert sst to numbers between 0 and 28, corresponding to the lut:
    data = np.ma.where(np.less(arr, 0), 28, 28.0 - arr)
    data = np.ma.where(np.greater(arr, 23.0), 4, data).round().astype('uint8')

    from trollimage.image import Image
    from satpy.imageo import palettes
    palette = palettes.sstlut_osisaf_metno()

    img = Image(data, mode='P', palette=palette)
    img.show()
    img.save('osisaf_sst_viirs_satpy.png')

    from pycoast import ContourWriter

    cw_ = ContourWriter('/home/a000680/data/shapes')
    pilim = img.pil_image()
    area_def = lcd['sea_surface_temperature'].info['area']
    cw_.add_coastlines(
        pilim, area_def, resolution='i', level=1, outline=(220, 220, 220))
    pilim.show()
    pilim.save('./osisaf_sst_viirs_satpy_withovl.png')
