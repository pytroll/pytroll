# -*-python-*- 
#

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

