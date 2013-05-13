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

"""Test reading just corners in HDF5 files.
"""

from mpop.satellites import PolarFactory
from datetime import datetime

t = datetime(2013, 3, 12, 10, 48)

tslots = [datetime(2013, 3, 12, 10, 34),
          datetime(2013, 3, 12, 10, 35),
          datetime(2013, 3, 12, 10, 37),
          datetime(2013, 3, 12, 10, 38),
          datetime(2013, 3, 12, 10, 40),
          datetime(2013, 3, 12, 10, 41),
          datetime(2013, 3, 12, 10, 43),
          datetime(2013, 3, 12, 10, 44),
          datetime(2013, 3, 12, 10, 45),
          datetime(2013, 3, 12, 10, 47),
          datetime(2013, 3, 12, 10, 48)
    ]

gs = []

for t in tslots:

    g = PolarFactory.create_scene("npp", "", "viirs", t, orbit="07108")
    
    g.load(g.image.green_snow.prerequisites | g.image.hr_overview.prerequisites
           | g.image.dnb.prerequisites)

    gs.append(g)

import mpop.scene

g = mpop.scene.assemble_segments(gs)

#l = g.project("worldeqc3km")

#l.image.green_snow().save("/tmp/gs_world.png")
#l.image.hr_overview().save("/tmp/ov_world.png")


l = g.project("euron1")

l.image.green_snow().save("/tmp/gs_euron1.png")
l.image.hr_overview().save("/tmp/ov_euron1.png")

l = g.project("scan")

l.image.green_snow().save("/tmp/gs_scan.png")
l.image.hr_overview().save("/tmp/ov_scan.png")

l = g.project("ssea250")

l.image.green_snow().save("/tmp/gs_ssea250.png")
l.image.hr_overview().save("/tmp/ov_ssea250.png")


