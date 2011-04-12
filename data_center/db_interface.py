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

"""An interface between the datacenter and the database.
"""


from hl_file import File
import pytroll_db as db
from dc.connections import DCConnectionsSub

def update(message):
    """Update the database if needed.
    """
    print "Got an update", message

    file_obj = File(message.data["filename"], dbm,
                    filetype=message.data.get("type", None),
                    fileformat=message.data.get("format", None))
    for key, val in message.data.items():
        if key == "filename":
            continue
        file_obj[key] = val

def request(message):
    pass


CASES = {"update": update,
         "request": request}

if __name__ == "__main__":
    
    dbm = db.DCManager('postgresql://a001673:@localhost.localdomain:5432/sat_db')
    dc = DCConnectionsSub().start()
    try:
        for msg in dc.receive(timeout=1):
            if not msg:
                continue
            CASES[msg.type](msg)

    except KeyboardInterrupt:
        print "terminating consumer..."
        dc.stop()
