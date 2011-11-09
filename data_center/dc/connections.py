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

"""Different kinds of connections to the datacenter. These classes collect
datacenter addresses for further use.
"""

import time
import zmq

from posttroll.address_receiver import getaddress
from posttroll.message import Message

class GenericConnections(object):
    """Datacenter connections manager.
    """
    def __init__(self, module_name):
        self._dc_addresses = getaddress(module_name)
        self._context = zmq.Context()
        self._connections = {}

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

class DCConnections(object):
    """Datacenter connections manager.
    """
    def __init__(self):
        self._dc_addresses = getaddress('dc')
        self._context = zmq.Context()
        self._connections = {}

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


class  DCConnectionsPush(DCConnections):

    def _make_connection(self, addr):
        """Activate a new connection.
        """
        sock = self._context.socket(zmq.PUSH)
        dest = 'tcp://' + addr[0] + ':%d' % addr[1]
        print 'connecting to', dest
        sock.connect(dest)
        return sock

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

    def send(self, msg):
        """Send message *msg* to all known datacenters
        """
        for sock in self._get_connections():
            print 'sending to', str(sock), "'%s'" % str(msg)
            sock.send(str(msg))

class  DCConnectionsSub(DCConnections):

    publisher_port = 21202

    def __init__(self):
        self._dc_addresses = getaddress('dc')
        self._context = zmq.Context()
        self.subscriber = self._context.socket(zmq.SUB)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "pytroll")
        self._connections = []
        self._loop = False

    def start(self):
        """Start datacenter address gathering.
        """
        self._dc_addresses.start()
        self._loop = True
        return self
    
    def stop(self):
        """Stop datacenter address gathering.
        """
        self._loop = False
        self._connections = [] 

    def _get_connections(self):
        """Do the datacenter address gathering.
        """
        ads = self._dc_addresses.get()
        for addr in ads:
            if addr not in self._connections:
                print "connecting to", addr
                self.subscriber.connect ("tcp://%s:%d"%(addr[0], self.publisher_port))
                self._connections.append(addr)
        

    def receive_simple(self, timeout=None):
        while True:
            self._get_connections()
            if self._connections:
                yield self.subscriber.recv()
            else:
                time.sleep(1)

    def receive(self, timeout=None):
        if timeout:
            timeout *= 1000.
        poller = zmq.Poller()
        poller.register(self.subscriber, zmq.POLLIN)
        try:
            while(self._loop):
                self._get_connections()
                try:
                    s = poller.poll(timeout=timeout)
                    if s:
                        if s[0][0] == self.subscriber:
                            m = Message.decode(self.subscriber.recv(zmq.NOBLOCK))
                            yield m
                        else:
                            print >>sys.stderr, "poller received a unknown subscriber"
                    else:
                        # timeout
                        yield None
                except zmq.ZMQError:
                    print >>sys.stderr, 'recveive failed'
        finally:
            poller.unregister(self.subscriber)
            self._dc_addresses.stop()
            self.subscriber.close()        
