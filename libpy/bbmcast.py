# Send/receive UDP multicast packets.
# Requires that your OS kernel supports IP multicast.
#
# This is based on python-examples Demo/sockets/mcast.py
#

MC_GROUP = '225.0.0.212' # 224.0.0.0 through 224.0.0.255 is reserved administrative tasks
TTL_LOCALNET = 1 # local network multicast (<32)

import sys
import time
import struct
from socket import *

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
    group = mcgroup
    if not mcgroup or gethostbyname(mcgroup) == '255.255.255.255':
        group = '<broadcast>'
        s = socket(AF_INET, SOCK_DGRAM)
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    else:
        s = socket(AF_INET, SOCK_DGRAM)
        ttl = struct.pack('b', TTL_LOCALNET) # Time-to-live
        s.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)
    return s, group

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
        
    def settimeout(self, timeout=None):
        # A timeout will throw a 'socket.timeout'
        self.socket.settimeout(timeout)
        return self

    def __call__(self):
        data, sender = self.socket.recvfrom(self.BUFSIZE)
        return data, sender

    def close(self):
        self.socket.close()

# Allow non-object interface
def mcast_receiver(port, mcgroup=MC_GROUP):
    # Open a UDP socket, bind it to a port and select a multicast group
 
    # Import modules used only here
    import string
    import struct

    group = mcgroup
    if not group or gethostbyname(group) == '255.255.255.255':
        group = None

    # Create a socket
    s = socket(AF_INET, SOCK_DGRAM)

    # Allow multiple copies of this program on one machine
    # (not strictly needed)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    if group:
        s.setsockopt(SOL_IP, IP_MULTICAST_TTL, TTL_LOCALNET) # default
        s.setsockopt(SOL_IP, IP_MULTICAST_LOOP, 1) # default

    # Bind it to the port
    s.bind(('', port))

    # Look up multicast group address in name server
    # (doesn't hurt if it is already in ddd.ddd.ddd.ddd format)
    if group:
        group = gethostbyname(group)

        # Construct binary group address
        bytes = map(int, string.split(group, "."))
        grpaddr = 0
        for byte in bytes: grpaddr = (grpaddr << 8) | byte

        # Construct struct mreq from grpaddr and ifaddr
        ifaddr = INADDR_ANY
        mreq = struct.pack('LL', htonl(grpaddr), htonl(ifaddr))

        # Add group membership
        s.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)
        
    if not group:
        group = '<broadcast>'
    return s, group

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
    def sender(mcgroup):
        send = MulticastSender(PORT, mcgroup)
        while 1:
            data = repr(time.time())
            print data
            send(data)
            time.sleep(1)


    # Receiver subroutine (as many as you like)
    def receiver(mcgroup):
        # Open and initialize the socket
        recv = MulticastReceiver(PORT, mcgroup)
        # Loop, printing any data we receive
        while 1:
            data, sender = recv()
            while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
            print sender, ':', repr(data)

    PORT = 8123
    mcgroup = MC_GROUP
    opts, args = getopt.getopt(sys.argv[1:], "mb")
    for k, v in opts:
        if k == '-b':
            mcgroup = None
    if not args:
        usage()
    what = args[0]
    if what == 'send':
        sender(mcgroup)
    elif what == 'recv':
        receiver(mcgroup)
    else:
        usage()
