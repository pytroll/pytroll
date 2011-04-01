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

"""A very stupid producer.
"""

from posttroll.address_receiver import AddressReceiver
from posttroll.message import Message

import datetime
import time
import zmq

ADDRESSES = AddressReceiver("dc")

ADDRESSES.start()

current_addresses = set()
sockets = []

try:
    while True:
        got_addresses = set(ADDRESSES.get())
        new_addresses = got_addresses - current_addresses
        
        for server in new_addresses:
            print datetime.datetime.now()
            print "New datacenter detected:", str(server)
            socket = zmq.Context().socket(zmq.PUSH)
            socket.connect("tcp://"+server[0]+":"+str(server[1]))
            sockets.append(socket)

        current_addresses |= new_addresses
        for socket in sockets:
            msg = "the time is now: " + str(datetime.datetime.now())
            print "Sending:", msg
            message = Message('/test/clock', 'info', data=msg)
            rawstr = message.encode()
            socket.send(rawstr)
        
        
        time.sleep(1)
except KeyboardInterrupt:
    print "terminating producer..."
    ADDRESSES.stop()

