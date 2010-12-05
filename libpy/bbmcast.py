# Send/receive UDP multicast packets.
# Requires that your OS kernel supports IP multicast.
#
# This is based on python-examples Demo/sockets/mcast.py
#

MC_GROUP = '225.0.0.250' # 224.0.0.0 through 224.0.0.255 is reserved administrative tasks
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

    def __init__(self, port, broadcast=False):
        s = socket(AF_INET, SOCK_DGRAM)
        if broadcast:
            s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            group = '<broadcast>'
        else:
            group = MC_GROUP
            ttl = struct.pack('b', TTL_LOCALNET) # Time-to-live
            s.setsockopt(IPPROTO_IP, IP_MULTICAST_TTL, ttl)
        self.port = port
        self.group = group
        self.socket = s

    def __call__(self, data):
        self.socket.sendto(data, (self.group, self.port))

    def close(self):
        self.socket.close()

#-----------------------------------------------------------------------------
#
# Receiver.
#
#-----------------------------------------------------------------------------
class MulticastReceiver(object):
    
    BUFSIZE = 1024
    def __init__(self, port):
        self.port = port
        self.socket = _openmcastsock(MC_GROUP, port)
        
    def settimeout(self, timeout=None):
        # A timeout will throw a 'socket.timeout'
        self.socket.settimeout(timeout)
        return self

    def __call__(self):
        data, sender = self.socket.recvfrom(self.BUFSIZE)
        return data, sender

    def close(self):
        self.socket.close()

#-----------------------------------------------------------------------------
#
# Miscellaneous.
#
#-----------------------------------------------------------------------------
def _openmcastsock(group, port):
    # Open a UDP socket, bind it to a port and select a multicast group

    # Import modules used only here
    import string
    import struct

    # Create a socket
    s = socket(AF_INET, SOCK_DGRAM)

    # Allow multiple copies of this program on one machine
    # (not strictly needed)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.setsockopt(SOL_IP, IP_MULTICAST_TTL, TTL_LOCALNET) # default
    s.setsockopt(SOL_IP, IP_MULTICAST_LOOP, 1) # default

    # Bind it to the port
    s.bind(('', port))

    # Look up multicast group address in name server
    # (doesn't hurt if it is already in ddd.ddd.ddd.ddd format)
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

    return s

#-----------------------------------------------------------------------------
#
# Test
#
#-----------------------------------------------------------------------------
if __name__ == '__main__':

    def usage():
        print """Usage: bbmcast -s (sender)
       bbmcast -b (sender, using broadcast instead of multicast)
       bbmcast    (receivers)"""
        sys.exit(2)

    # Sender subroutine (only one per local area network ... NOT)
    def sender(broadcast=False):
        s = MulticastSender(PORT, broadcast=broadcast)
        while 1:
            data = repr(time.time())
            print data
            s(data)
            time.sleep(1)


    # Receiver subroutine (as many as you like)
    def receiver():
        # Open and initialize the socket
        s = MulticastReceiver(PORT).settimeout(None)

        # Loop, printing any data we receive
        while 1:
            data, sender = s()
            while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
            print sender, ':', repr(data)

    PORT = 8123
    flags = sys.argv[1:]
    if flags:
        if flags[0] not in ('-b', '-s'):
            usage()
        broadcast = flags[0] == '-b'
        sender(broadcast)
    else:
        receiver()
