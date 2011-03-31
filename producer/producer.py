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

import time
import zmq

from pytroll.message import Message
from pytroll.address_receiver import getaddress

class DCConnections:

    _context = zmq.Context()

    def __init__(self):
        self._dc_addresses = getaddress('dc')
        self._connections = {}

    def send(self, msg):
        for c in self._get_connections():
            print 'sending to', str(c), "'%s'"%`msg`
            c.send(`msg`)

    def start(self):
        self._dc_addresses.start()
        return self
    
    def stop(self):
        self._dc_addresses.stop()
        for s in self._connections.values():
            s.close()
        self._connections = {}

    def _get_connections(self):
        ads = self._dc_addresses.get()
        for a in ads:
            if a not in self._connections.keys():
                self._connections[a] = self._make_connection(a)
        # remove old DC connection
        for a, c in self._connections.items():
            if a not in ads:
                try:
                    c.close()
                except:
                    pass
                del self._connections[a]
        return self._connections.values()

    def _make_connection(self, addr):
        s = self._context.socket(zmq.PUSH)
        dest = 'tcp://' + addr[0] + ':%d'%addr[1]
        print 'connecting to', dest
        s.connect(dest)
        return s



class Messager:
    def __init__(self):
        self.count = 0
    def __call__(self):
        self.count += 1        
        return Message('/test/1/2/3', 'info', "what's up doc #%d"%self.count)

connections = DCConnections().start()
msg = Messager()
while True:
    try:
        connections.send(msg())
        time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print "quitting ..."
        connections.stop()
        break
