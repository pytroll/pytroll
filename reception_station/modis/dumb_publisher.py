#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, 2014 SMHI

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

"""Testing publishing from posttroll.
"""

from posttroll.publisher import Publish
from posttroll.message import Message
from time import sleep
from datetime import datetime

msgs = [
    """pytroll://PDS/0/norrköping/dev/polar/direct_readout safusr.u@lxserv248.smhi.se file {u'satellite': u'TERRA', u'format': u'PDS', u'start_time': datetime.datetime(2014, 8, 27, 7, 57, 53), u'level': u'0', u'orbit_number': 78142, u'uri': u'ssh://safe.smhi.se//san1/polar_in/direct_readout/eos/lvl0/P0420064AAAAAAAAAAAAAA14239075753001.PDS', u'number': 1, u'instrument': u'modis', u'end_time': datetime.datetime(2014, 8, 27, 8, 8, 35), u'filename': u'P0420064AAAAAAAAAAAAAA14239075753001.PDS', u'type': u'binary'}""",
    """pytroll://PDS/0/norrköping/dev/polar/direct_readout safusr.u@lxserv248.smhi.se file {u'satellite': u'TERRA', u'format': u'PDS', u'start_time': datetime.datetime(2014, 8, 27, 7, 57, 53), u'level': u'0', u'orbit_number': 78142, u'uri': u'ssh://safe.smhi.se//san1/polar_in/direct_readout/eos/lvl0/P0420064AAAAAAAAAAAAAA14239075753000.PDS', u'number': 0, u'instrument': u'modis', u'end_time': datetime.datetime(2014, 8, 27, 8, 8, 35), u'filename': u'P0420064AAAAAAAAAAAAAA14239075753000.PDS', u'type': u'binary'}""",

    # """pytroll://PDS/0/norrköping/dev/polar/direct_readout file safusr.u@lxserv248.smhi.se 2014-08-25T02:17:46.213527 v1.01 application/json {"satellite": "AQUA", "uri": "ssh://safe.smhi.se//san1/polar_in/direct_readout/eos/lvl0/P15409571540958154095914237020910000.PDS", "format": "PDS", "start_time": "2014-08-25T02:09:10", "level": "0", "orbit_number": 65470, "number": 0, "filename": "P15409571540958154095914237020910000.PDS", "instrument": "gbad", "end_time": "2014-08-25T02:13:46", "type": "binary"}""",
    # """pytroll://PDS/0/norrköping/dev/polar/direct_readout file safusr.u@lxserv248.smhi.se 2014-08-25T02:17:35.385819 v1.01 application/json {"satellite": "AQUA", "uri": "ssh://safe.smhi.se//san1/polar_in/direct_readout/eos/lvl0/P15409571540958154095914237020910001.PDS", "format": "PDS", "start_time": "2014-08-25T02:09:10", "level": "0", "orbit_number": 65470, "number": 1, "filename": "P15409571540958154095914237020910001.PDS", "instrument": "gbad", "end_time": "2014-08-25T02:13:46", "type": "binary"}""",
    # """pytroll://PDS/0/norrköping/dev/polar/direct_readout file safusr.u@lxserv248.smhi.se 2014-08-25T02:17:00.092837 v1.01 application/json {"satellite": "AQUA", "uri": "ssh://safe.smhi.se//san1/polar_in/direct_readout/eos/lvl0/P1540064AAAAAAAAAAAAAA14237020910000.PDS", "format": "PDS", "start_time": "2014-08-25T02:09:10", "level": "0", "orbit_number": 65470, "number": 0, "filename": "P1540064AAAAAAAAAAAAAA14237020910000.PDS", "instrument": "modis", "end_time": "2014-08-25T02:13:46", "type": "binary"}""",
    # """pytroll://PDS/0/norrköping/dev/polar/direct_readout file safusr.u@lxserv248.smhi.se 2014-08-25T02:17:36.588966 v1.01 application/json {"satellite": "AQUA", "uri": "ssh://safe.smhi.se//san1/polar_in/direct_readout/eos/lvl0/P1540064AAAAAAAAAAAAAA14237020910001.PDS", "format": "PDS", "start_time": "2014-08-25T02:09:10", "level": "0", "orbit_number": 65470, "number": 1, "filename": "P1540064AAAAAAAAAAAAAA14237020910001.PDS", "instrument": "modis", "end_time": "2014-08-25T02:13:46", "type": "binary"}""",
]

with Publish("receiver", 0, ["PDS", ]) as pds_pub:
    while True:
        # msg = Message('/oper/polar/direct_readout/norrköping', "info",
        # "the time is now " + str(datetime.now())).encode()
        # idx = np.random.randint(0,3)
        # msg = TEST_MSG[idx]
        # hrpt_pub.send(msg)
        # pds_pub.send(msg)
        # print msg
        for msg in msgs:
            pds_pub.send(msg)
            sleep(3)

        sleep(30)
        # msg = Message('/oper/polar/direct_readout/norrköping', "info",
        #               "the time is now " + str(datetime.now())).encode()
        # pds_pub.send(msg)
        # print msg
        # sleep(0.5)
