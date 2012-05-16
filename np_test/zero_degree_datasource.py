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

"""A datasource for msg hrit data.
"""

from posttroll.publisher import Publish
from posttroll.message import Message
import time
from datetime import datetime, timedelta
import glob
import os

PATH = "/data/24/saf/geo_in"

PATTERN = "H-000-MSG*"

stamp = datetime.utcnow() - timedelta(hours=1)

def get_file_list(timestamp):
    """Get files.
    """
    flist = glob.glob(os.path.join(PATH, PATTERN))
    result = []
    for fil in flist:
        if not os.path.isfile(fil):
            continue
        mtime = os.stat(fil).st_mtime
        dt_ = datetime.utcfromtimestamp(mtime)        
        if timestamp < dt_:
            result.append((fil, dt_))

    return sorted(result, lambda x, y: cmp(x[1], y[1]))

def younger_than_stamp_files():
    """Uses glob polling to get new files.
    """

    global stamp
    for fil, tim in get_file_list(stamp):
        yield os.path.join(PATH, fil)
        stamp = tim

def send_new_files():
    """Create messages and send away.
    """
    for fil in younger_than_stamp_files():
        base = os.path.basename(fil)
        elements = [item.strip("_") for item in base.split("-")]
        metadata = {
            "filename": base,
            "URIs": ["file://"+fil],
            "type": "HRIT lvl1.5",
            "format": "HRIT",
            "satellite_name": elements[3],
            "channel_name": elements[4],
            "segment_number": elements[5],
            "compressed": elements[-1] == "C",
            "time_start": datetime.strptime(elements[6],
                                            "%Y%m%d%H%M").isoformat()}
        import pprint
        pprint.pprint(metadata)
        yield Message('/oper/geo/0deg', 'file', metadata)


/oper/geo/rss
/test/polar/regional/norrköping
/dev
/db
try:
    with Publish("zero_degree_datasource", "HRIT lvl1.5", 9010) as pub:
        time.sleep(10)
        while True:
            for i in send_new_files():
                print "publishing " + str(i)
                pub.send(str(i))
            time.sleep(30)
except KeyboardInterrupt:
    print "terminating datasource..."
