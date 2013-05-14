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

tslot = datetime(2013, 3, 12, 10, 45)

tstart = datetime(2013, 3, 12, 10, 39)
tend = datetime(2013, 3, 12, 10, 45)

g = PolarFactory.create_scene("npp", "", "viirs", tslot, orbit="07108")
    
g.load(g.image.green_snow.prerequisites | g.image.hr_overview.prerequisites
       | g.image.dnb.prerequisites) # time_interval=(tstart,tend))


