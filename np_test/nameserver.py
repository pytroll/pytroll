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

"""Manage other's subscriptions.
"""

from posttroll.connections import GenericConnections
import zmq

GC = GenericConnections("")
GC.start()
port = 5555

def get_address(data_type):
    """Get the address of the module for a given *data_type*.
    """
    if data_type == "":
        return str(GC.get_addresses())
    # a tuple should be returned...
    for addr in GC.get_addresses():
        if addr["type"] == data_type:
            return addr["URI"]
    return ""

try:
    context = zmq.Context()
    listener = context.socket(zmq.REP)
    listener.bind("tcp://*:"+str(port))
    while True:
        msg = listener.recv()
        listener.send_unicode(get_address(msg))

except KeyboardInterrupt:
    # this is needed for the reception to be interruptible
    pass

finally:
    print "terminating nameserver..."
    GC.stop()
    listener.close()

