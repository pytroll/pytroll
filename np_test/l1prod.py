#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011, 2014.

# Author(s):
 
#   Martin Raspaud <martin.raspaud@smhi.se>

# This file is part of pytroll.

# Pytroll is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# Pytroll is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# pytroll.  If not, see <http://www.gnu.org/licenses/>.

""" Dummy level 1b datasource 
"""

from posttroll.publisher import Publish
from posttroll.message import Message
import time
from datetime import datetime, timedelta

data_type1 = "EOS/1"
data_type2 = "HRPT/1b"


try:
    counter = 0
    with Publish("l1prod", 0, [data_type2]) as PUB:
        while True:
            time.sleep(5)
            msg = 'pytroll://EOS/1/norrkoping/oper/polar/direct_readout file safusr.u@lxserv248.smhi.se 2012-10-15T08:22:09.098804 v1.01 application/json {"satellite": "TERRA", "format": "EOS", "start_time": "2012-10-15T09:40:19", "level": "1", "orbit_number": 68226, "uri": "ssh://safe.smhi.se//data/proj/safutv/data/polar_out/direct_readout/modis/MOD021km_A12289_094019_2012289095628.hdf", "filename": "MOD021km_A12289_094019_2012289095628.hdf", "instrument": "modis", "type": "HDF4"}'

            print "publishing " + str(msg)
            PUB.send(str(msg))

except KeyboardInterrupt:
    print "terminating datasource..."





