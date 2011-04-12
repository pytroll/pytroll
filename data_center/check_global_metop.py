#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011.

# Author(s):
 
#   Lars Ø. Rasmussen <ras@dmi.dk>
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

"""A simple producer.
"""

import time
from datetime import datetime, timedelta
import glob
import os

from posttroll.message import Message
from dc.connections import DCConnectionsPush

PATH = "/data/prod/satellit/metop"

PATTERN = "AVHR_xxx_1B_M02_*"

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
        metadata = {
            "URIs": ["file://"+fil],
            "type": "HRPT 1b",
            "format": "EPS 1b",
            "time_of_first_scanline": datetime.strptime(base[16:30],
                                                        "%Y%m%d%H%M%S").isoformat(),
            "time_of_last_scanline": datetime.strptime(base[32:46],
                                                        "%Y%m%d%H%M%S").isoformat()}
        import pprint
        pprint.pprint(metadata)
        yield Message('/dc/polar/gds', 'update', metadata)
        

if __name__ == '__main__':
    CONNECTIONS = DCConnectionsPush().start()
    # wait to get a connection
    time.sleep(3)
    while True:
        try:
            #send_new_files()
            for i in send_new_files():
                CONNECTIONS.send(i)
            time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            print "quitting ..."
            CONNECTIONS.stop()
            break
