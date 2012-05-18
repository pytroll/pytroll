#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011, 2012 SMHI

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
from posttroll.message import Message
import zmq

def get_address(data_type, gc):
    """Get the address of the module for a given *data_type*.
    """
    if data_type == "":
        return Message("/oper/ns", "info", gc.get_addresses())
    # a tuple should be returned...
    for addr in gc.get_addresses():
        if data_type in addr["type"]:
            return Message("/oper/ns", "info", addr)
    return Message("/oper/ns", "info", "")

if __name__ == '__main__':
    GC = GenericConnections("")
    GC.start()
    port = 5555

    try:
        context = zmq.Context()
        listener = context.socket(zmq.REP)
        listener.bind("tcp://*:"+str(port))
        while True:
            m = listener.recv()
            print m
            msg = Message.decode(m)
            listener.send_unicode(str(get_address(msg.data["type"], GC)))

    except KeyboardInterrupt:
        # this is needed for the reception to be interruptible
        pass

    finally:
        print "terminating nameserver..."
        GC.stop()
        listener.close()

