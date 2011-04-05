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
import zmq

from posttroll.message import Message
from posttroll.address_receiver import getaddress

class DCConnections:
    """Datacenter connections manager.
    """
    _context = zmq.Context()

    def __init__(self):
        self._dc_addresses = getaddress('dc')
        self._connections = {}

    def send(self, msg):
        """Send message *msg* to all known datacenters
        """
        for sock in self._get_connections():
            print 'sending to', str(sock), "'%s'" % str(msg)
            sock.send(str(msg))

    def start(self):
        """Start datacenter address gathering.
        """
        self._dc_addresses.start()
        return self
    
    def stop(self):
        """Stop datacenter address gathering.
        """
        self._dc_addresses.stop()
        for sock in self._connections.values():
            sock.close()
        self._connections = {}

    def _get_connections(self):
        """Do the datacenter address gathering.
        """
        ads = self._dc_addresses.get()
        for addr in ads:
            if addr not in self._connections.keys():
                self._connections[addr] = self._make_connection(addr)
        # remove old DC connection
        for addr, conn in self._connections.items():
            if addr not in ads:
                conn.close()
                del self._connections[addr]
        return self._connections.values()

    def _make_connection(self, addr):
        """Activate a new connection.
        """
        sock = self._context.socket(zmq.PUSH)
        dest = 'tcp://' + addr[0] + ':%d' % addr[1]
        print 'connecting to', dest
        sock.connect(dest)
        return sock



class Messager:
    """Dummy messager class.
    """
    def __init__(self):
        self.count = 0
    def __call__(self):
        self.count += 1        
        return Message('/test/1/2/3', 'info', "what's up doc #%d"%self.count)

if __name__ == '__main__':
    CONNECTIONS = DCConnections().start()
    MSG = Messager()
    while True:
        try:
            CONNECTIONS.send(MSG())
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print "quitting ..."
            CONNECTIONS.stop()
            break
