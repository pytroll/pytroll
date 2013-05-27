#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

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

"""Benchmarking the pytroll/mpop chain on 4 areas of different sizes and areas,
for different npp channels.
"""

from mpop.satellites import PolarFactory
from datetime import datetime
import mpop.scene
import gc
from mpop.utils import debug_on
debug_on()
tslots = [#datetime(2013, 3, 12, 10, 34),
          #datetime(2013, 3, 12, 10, 35),
          #datetime(2013, 3, 12, 10, 37),
          #datetime(2013, 3, 12, 10, 38),
          #datetime(2013, 3, 12, 10, 40),
          datetime(2013, 3, 12, 10, 41),
          #datetime(2013, 3, 12, 10, 43),
          #datetime(2013, 3, 12, 10, 44),
          #datetime(2013, 3, 12, 10, 45),
          #datetime(2013, 3, 12, 10, 47),
          #datetime(2013, 3, 12, 10, 48)
    ]


# import mpop.utils
# mpop.utils.debug_on()

# gs = []


# for t in tslots[5:6]:

#     g = PolarFactory.create_scene("npp", "", "viirs", t, orbit="07108")
    
#     g.load(g.image.green_snow.prerequisites | g.image.hr_overview.prerequisites
#            | g.image.dnb.prerequisites)

#     gs.append(g)

# import mpop.scene

# g = mpop.scene.assemble_segments(gs)

# l = g.project("worldeqc30km")

# l.image.green_snow().save("/tmp/gs_world.png")
# l.image.hr_overview().save("/tmp/ov_world.png")
# l.image.dnb().save("/tmp/dnb_world.png")


# l = g.project("euron1")

# l.image.green_snow().save("/tmp/gs_euron1.png")
# l.image.hr_overview().save("/tmp/ov_euron1.png")
# l.image.dnb().save("/tmp/dnb_euron1.png")

# l = g.project("scan")

# l.image.green_snow().save("/tmp/gs_scan.png")
# l.image.hr_overview().save("/tmp/ov_scan.png")
# l.image.dnb().save("/tmp/dnb_scan.png")

# l = g.project("ssea250")

# l.image.green_snow().save("/tmp/gs_ssea250.png")
# l.image.hr_overview().save("/tmp/ov_ssea250.png")
# l.image.dnb().save("/tmp/dnb_ssea250.png")

# # areas:

# """
# REGION: worldeqc30km {
#         NAME:       World in 3km, platecarree
#         PCS_ID:     plate_carree
#         PCS_DEF:    units=m, proj=eqc, ellps=WGS84
#         XSIZE:      820
#         YSIZE:      410
#         AREA_EXTENT: (-20037508.3428, -10018754.1714, 20037508.3428, 10018754.1714)
# };


# REGION: euron1 {
# 	NAME:		Northern Europe - 1km
# 	PCS_ID:		ps60wgs84
# 	PCS_DEF:	proj=stere,ellps=WGS84,lat_0=90,lon_0=0,lat_ts=60
# 	XSIZE:		3072
# 	YSIZE:		3072
# 	AREA_EXTENT:	(-1000000.0, -4500000.0, 2072000.0, -1428000.0)

# };

# REGION: ssea250 {
#         NAME:		South Baltic Sea
# 	PCS_ID: 	merc
# 	PCS_DEF:	proj=merc,ellps=WGS84,lat_ts=0,lon_0=15
# 	XSIZE:		4096
# 	YSIZE:		4096
# 	AREA_EXTENT:    (-801407.36204689811, 7003690.6636438016, 1246592.6379531019, 9051690.6636438016)
# };

# REGION: scan {
# 	NAME:		Scandinavia
# 	PCS_ID:		ps60n
# 	PCS_DEF:	proj=stere,ellps=bessel,lat_0=90,lon_0=14,lat_ts=60
# 	XSIZE:		512
# 	YSIZE:		512
# 	AREA_EXTENT:	(-1268854.1266382949, -4150234.8425892727, 779145.8733617051, -2102234.8425892727)
# };


# """

t_start = datetime(2013, 3, 12, 10, 41)
t_end = datetime(2013, 3, 12, 10, 44)
@profile
def main():

    g = PolarFactory.create_scene("npp", "", "viirs", t_start, orbit="07108")

    #g.load(g.image.green_snow.prerequisites | g.image.hr_overview.prerequisites
    #              | g.image.dnb.prerequisites | g.image.truecolor.prerequisites, time_interval=(t_start, t_end))
    g.load(["I01"])       
    gc.collect()

    #l = g.project("worldeqc30km")
    l = g.project("scan")
    gc.collect()
    #l["I01"].show()
    #l.image.truecolor().show()
    return
    # l.image.green_snow().save("/tmp/gs_world.png")
    # l.image.hr_overview().save("/tmp/ov_world.png")
    # l.image.dnb().save("/tmp/dnb_world.png")

    # del l
    # gc.collect()
    # l = g.project("euron1")
    # gc.collect()

    # l.image.green_snow().save("/tmp/gs_euron1.png")
    # l.image.hr_overview().save("/tmp/ov_euron1.png")
    # l.image.dnb().save("/tmp/dnb_euron1.png")

    # del l
    gc.collect()
    l = g.project("scan")
    gc.collect()

    l.image.green_snow().save("/tmp/gs_scan.png")
    l.image.hr_overview().save("/tmp/ov_scan.png")
    l.image.dnb().save("/tmp/dnb_scan.png")

    del l
    gc.collect()
    l = g.project("ssea250")
    gc.collect()

    l.image.green_snow().save("/tmp/gs_ssea250.png")
    l.image.hr_overview().save("/tmp/ov_ssea250.png")
    l.image.dnb().save("/tmp/dnb_ssea250.png")

main()
raw_input("end")
# # areas:

# """
# REGION: worldeqc30km {
#         NAME:       World in 3km, platecarree
#         PCS_ID:     plate_carree
#         PCS_DEF:    units=m, proj=eqc, ellps=WGS84
#         XSIZE:      820
#         YSIZE:      410
#         AREA_EXTENT: (-20037508.3428, -10018754.1714, 20037508.3428, 10018754.1714)
# };


# REGION: euron1 {
# 	NAME:		Northern Europe - 1km
# 	PCS_ID:		ps60wgs84
# 	PCS_DEF:	proj=stere,ellps=WGS84,lat_0=90,lon_0=0,lat_ts=60
# 	XSIZE:		3072
# 	YSIZE:		3072
# 	AREA_EXTENT:	(-1000000.0, -4500000.0, 2072000.0, -1428000.0)

# };

# REGION: ssea250 {
#         NAME:		South Baltic Sea
# 	PCS_ID: 	merc
# 	PCS_DEF:	proj=merc,ellps=WGS84,lat_ts=0,lon_0=15
# 	XSIZE:		4096
# 	YSIZE:		4096
# 	AREA_EXTENT:    (-801407.36204689811, 7003690.6636438016, 1246592.6379531019, 9051690.6636438016)
# };

# REGION: scan {
# 	NAME:		Scandinavia
# 	PCS_ID:		ps60n
# 	PCS_DEF:	proj=stere,ellps=bessel,lat_0=90,lon_0=14,lat_ts=60
# 	XSIZE:		512
# 	YSIZE:		512
# 	AREA_EXTENT:	(-1268854.1266382949, -4150234.8425892727, 779145.8733617051, -2102234.8425892727)
# };


# """

