#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011.

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

data_type1 = "HRPT 1b"
data_type2 = "HRPT 1c"

try:
    counter = 0
    with Publish("l1prod", [data_type1, data_type2] , '9002') as PUB:
        while True:
            counter += 1
            msg1 = Message('/oper/hrpt', 'file', {"type": data_type1,
                                                "source": "dummy",
                                                "timestamp": str(datetime.utcnow())})
            msg2 = Message('/oper/hrpt', 'file', {"type": data_type2,
                                                "source": "dummy",
                                                "timestamp": str(datetime.utcnow())})
            print "publishing " + str(msg1)
            PUB.send(str(msg1))
            print "publishing " + str(msg2)
            PUB.send(str(msg2))
            time.sleep(5)

except KeyboardInterrupt:
    print "terminating datasource..."





