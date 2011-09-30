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

"""Send/receive UDP multicast packets.
Requires that your OS kernel supports IP multicast.

This is based on python-examples Demo/sockets/mcast.py
"""

__all__ = ('MulticastSender', 'MulticastReceiver', 'mcast_sender',
           'mcast_receiver', 'SocketTimeout')

# 224.0.0.0 through 224.0.0.255 is reserved administrative tasks
MC_GROUP = '225.0.0.212'

# local network multicast (<32)
TTL_LOCALNET = 1

import sys
import time
import struct
from socket import (socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_REUSEADDR,
                    SO_BROADCAST, IPPROTO_IP, IP_ADD_MEMBERSHIP, INADDR_ANY,
                    IP_MULTICAST_TTL, IP_MULTICAST_LOOP, SOL_IP, timeout,
                    gethostbyname, htonl)

SocketTimeout = timeout # for easy access to socket.timeout

#-----------------------------------------------------------------------------
#
# Sender.
#
#-----------------------------------------------------------------------------
class MulticastSender(object):

    def __init__(self, port, mcgroup=MC_GROUP):
        self.port = port
        self.group = mcgroup
        self.socket, self.group = mcast_sender(mcgroup)

    def __call__(self, data):
        self.socket.sendto(data, (self.group, self.port))

    def close(self):
        self.socket.close()

# Allow non-object interface
def mcast_sender(mcgroup=MC_GROUP):
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    if _is_broadcast_group(mcgroup):
        group = '<broadcast>'
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    elif((int(mcgroup.split(".")[0]) > 239) or 
         (int(mcgroup.split(".")[0]) < 224)):
        raise IOError("Invalid multicast address.")
    else:
        group = mcgroup
        ttl = struct.pack('b', TTL_LOCALNET) # Time-to-live
        sock.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)
    return sock, group

#-----------------------------------------------------------------------------
#
# Receiver.
#
#-----------------------------------------------------------------------------
class MulticastReceiver(object):
    
    BUFSIZE = 1024
    def __init__(self, port, mcgroup=MC_GROUP):
        # Note: a multicast receiver will also receive broadcast on same port.
        self.port = port
        self.socket, self.group = mcast_receiver(port, mcgroup)
        
    def settimeout(self, tout=None):
        # A timeout will throw a 'socket.timeout'
        self.socket.settimeout(tout)
        return self

    def __call__(self):
        data, sender = self.socket.recvfrom(self.BUFSIZE)
        return data, sender

    def close(self):
        self.socket.close()

# Allow non-object interface
def mcast_receiver(port, mcgroup=MC_GROUP):
    # Open a UDP socket, bind it to a port and select a multicast group
 
    if _is_broadcast_group(mcgroup):
        group = None
    else:
        group = mcgroup

    # Create a socket
    sock = socket(AF_INET, SOCK_DGRAM)

    # Allow multiple copies of this program on one machine
    # (not strictly needed)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    if group:
        sock.setsockopt(SOL_IP, IP_MULTICAST_TTL, TTL_LOCALNET) # default
        sock.setsockopt(SOL_IP, IP_MULTICAST_LOOP, 1) # default

    # Bind it to the port
    sock.bind(('', port))

    # Look up multicast group address in name server
    # (doesn't hurt if it is already in ddd.ddd.ddd.ddd format)
    if group:
        group = gethostbyname(group)

        # Construct binary group address
        bytes_ = [int(b) for b in group.split(".")]
        grpaddr = 0
        for byte in bytes_:
            grpaddr = (grpaddr << 8) | byte

        # Construct struct mreq from grpaddr and ifaddr
        ifaddr = INADDR_ANY
        mreq = struct.pack('LL', htonl(grpaddr), htonl(ifaddr))

        # Add group membership
        sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
        
    return sock, group or '<broadcast>'

#-----------------------------------------------------------------------------
#
# Small helpers.
#
#-----------------------------------------------------------------------------
def _is_broadcast_group(group):
    if not group or gethostbyname(group) in ('0.0.0.0', '255.255.255.255'):
        return True
    return False

#-----------------------------------------------------------------------------
#
# Test
#
#-----------------------------------------------------------------------------
if __name__ == '__main__':
    import getopt

    def usage():
        print """Usage: bbmcast [-m|b] [send|recv]
       -m, using multicast <default>
       -b, using broadcast"""
        sys.exit(2)

    # Sender subroutine (only one per local area network ... NOT)
    def do_send(mcgroup):
        send = MulticastSender(PORT, mcgroup)
        while 1:
            data = repr(time.time())
            print data
            send(data)
            time.sleep(1)


    # Receiver subroutine (as many as you like)
    def do_receive(mcgroup):
        # Open and initialize the socket
        recv = MulticastReceiver(PORT, mcgroup)
        # Loop, printing any data we receive
        while 1:
            data, sender = recv()
            while data[-1:] == '\0':
                data = data[:-1] # Strip trailing \0's
            print sender, ':', repr(data)

    PORT = 21200
    grp = MC_GROUP
    opts, args = getopt.getopt(sys.argv[1:], "mb")
    for k, v in opts:
        if k == '-b':
            grp = None
    if not args:
        usage()
    what = args[0]
    if what == 'send':
        do_send(grp)
    elif what == 'recv':
        do_receive(grp)
    else:
        usage()
