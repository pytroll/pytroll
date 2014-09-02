#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Adam.Dybbroe

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

"""Ingest RDR messages/files for testing
"""

from posttroll.publisher import Publish
from posttroll.message import Message
import time
import os.path

import os
MODE = os.getenv("SMHI_MODE")
if MODE is None:
    MODE = "dev"


files = [
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1218126_e1218250_b00001_c20140902121954389000_nfts_drl.h5",
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1218268_e1219504_b00001_c20140902122117716000_nfts_drl.h5",
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1219522_e1221141_b00001_c20140902122243267000_nfts_drl.h5",
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1221158_e1222395_b00001_c20140902122408304000_nfts_drl.h5",
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1222412_e1224050_b00001_c20140902122533865000_nfts_drl.h5",
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1224066_e1225285_b00001_c20140902122659405000_nfts_drl.h5",
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1225320_e1226557_b00001_c20140902122824964000_nfts_drl.h5",
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1226575_e1228211_b00001_c20140902122950014000_nfts_drl.h5",
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1228230_e1229465_b00001_c20140902123115489000_nfts_drl.h5",
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1229483_e1231120_b00001_c20140902123241072000_nfts_drl.h5",
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1231137_e1232373_b00001_c20140902123315002000_nfts_drl.h5",
    "/san1/polar_in/direct_readout/npp/lvl0/RNSCA-RVIRS_npp_d20140902_t1232391_e1232515_b00001_c20140902123315119000_nfts_drl.h5",

]


# message = 'pytroll://oper/polar/direct_readout/norrköping file safusr.u@lxserv248.smhi.se 2013-04-23T01:13:11.979056 v1.01 application/json {"satellite": "NPP", "format": "RDR", "start_time": "2013-04-23T00:55:23", "level": "0", "orbit_number": 7699, "uri": "ssh://nimbus/archive/npp/RNSCA-RVIRS_npp_d20130423_t0055217_e0110433_b00001_c20130423011303651000_nfts_drl.h5", "filename": "RNSCA-RVIRS_npp_d20130423_t0055217_e0110433_b00001_c20130423011303651000_nfts_drl.h5", "instrument": "viirs", "end_time": "2013-04-23T01:10:53", "type": "HDF5"}'

def get_rdr_times(filename):
    from datetime import datetime, timedelta

    bname = os.path.basename(filename)
    sll = bname.split('_')
    start_time = datetime.strptime(sll[2] + sll[3][:-1],
                                   "d%Y%m%dt%H%M%S")
    end_time = datetime.strptime(sll[2] + sll[4][:-1],
                                 "d%Y%m%de%H%M%S")
    if end_time < start_time:
        end_time += timedelta(days=1)
    return start_time, end_time


def create_rdr_message(filename):

    data = {}
    data["satellite"] = "NPP"
    data["format"] = "RDR"
    data["instrument"] = "viirs"
    data["type"] = "HDF5"
    data["level"] = "0"
    data["orbit_number"] = "00001"
    data["start_time"], data["end_time"] = get_rdr_times(filename)
    data["filename"] = os.path.basename(filename)
    data["uri"] = "ssh://safe.smhi.se" + filename
    #msg = Message("/oper/polar/direct_readout/norrköping", "file", data)
    environment = MODE
    msg = Message('/' + data['format'] + '/' + data['level'] +
                  '/norrköping/' + environment + '/polar/direct_readout/',
                  "file", data).encode()
    print "Publishing", msg
    return msg

try:
    with Publish("receiver", 0) as pub:
        for filename in files:
            message = create_rdr_message(filename)
            print "publishing", message
            pub.send(str(message))
            time.sleep(86)
            # time.sleep(200)
            # time.sleep(2)

except KeyboardInterrupt:
    print "terminating publisher..."
