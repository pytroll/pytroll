#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011 SMHI

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

"""
"""

from datetime import datetime
from posttroll.message import Message
from posttroll.publisher import Publisher, get_own_ip
from posttroll.message_broadcaster import sendaddresstype
import time

PUB_ADDRESS = "tcp://" + str(get_own_ip()) + ":9005"
BROADCASTER = sendaddresstype('dummy_datasource', PUB_ADDRESS, "NWP", 2).start()

PUB = Publisher(PUB_ADDRESS)

oper
test
dev
db

"""
/oper/polar/direct_readout/norrköping
/oper/polar/regional/kangerlusuaq
/oper/geo/0deg
/oper/geo/rss
/oper/geo/iodc
/oper/geo/iodc
"""

try:
    counter = 0
    while True:
        counter += 1
        msg = Message('/oper/nwp', 'file', {"type": "NWP",
                                            "source": "hirlam",
                                            "timestamp": str(datetime.utcnow())})
        print "publishing " + str(msg)
        PUB.send(str(msg))
        time.sleep(5)
except KeyboardInterrupt:
    print "terminating datasource..."
    BROADCASTER.stop()
    PUB.stop()
