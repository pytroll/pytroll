#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c14526.ad.smhi.se>

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

"""Test reading VIIRS SDR data in segments given by start and end time
"""

from mpop.satellites import PolarFactory
from datetime import datetime
from mpop.utils import debug_on
debug_on()

# Test case:
#tslot = datetime(2013, 3, 12, 10, 45)
#tstart = datetime(2013, 3, 12, 10, 39)
#tend = datetime(2013, 3, 12, 10, 45)

#g = PolarFactory.create_scene("npp", "", "viirs", tslot, orbit="07108")

# Adam's test case:
tslot = datetime(2013, 4, 25, 11, 57)
tstart = datetime(2013, 4, 25, 11, 55)
tend = datetime(2013, 4, 25, 12, 1)

g = PolarFactory.create_scene("npp", "", "viirs", tslot, orbit="07734")
    
g.load(g.image.green_snow.prerequisites | g.image.hr_overview.prerequisites
       | g.image.dnb.prerequisites, time_interval=(tstart,tend))
#g.load([8.6])


"""
tslots = [datetime(2013, 4, 25, 11, 53),
          datetime(2013, 4, 25, 11, 55),
          datetime(2013, 4, 25, 11, 56),
          datetime(2013, 4, 25, 11, 58),
          datetime(2013, 4, 25, 11, 59),
          datetime(2013, 4, 25, 12, 0)
          ]


gs = []

for t in tslots:

    g = PolarFactory.create_scene("npp", "", "viirs", t, orbit="07734")
    
    g.load(g.image.green_snow.prerequisites | g.image.hr_overview.prerequisites | g.image.dnb.prerequisites)

    gs.append(g)

import mpop.scene

g = mpop.scene.assemble_segments(gs)
"""

#raw_input('Waiting - press any key')




"""
l = g.project("worldeqc30km")

l.image.green_snow().save("gs_world.png")
l.image.hr_overview().save("ov_world.png")
l.image.dnb().save("dnb_world.png")


l = g.project("euron1")

l.image.green_snow().save("gs_euron1.png")
l.image.hr_overview().save("ov_euron1.png")
l.image.dnb().save("dnb_euron1.png")

l = g.project("scan")

l.image.green_snow().save("gs_scan.png")
l.image.hr_overview().save("ov_scan.png")
l.image.dnb().save("dnb_scan.png")

l = g.project("ssea250")

l.image.green_snow().save("gs_ssea250.png")
l.image.hr_overview().save("ov_ssea250.png")
l.image.dnb().save("dnb_ssea250.png")
"""

