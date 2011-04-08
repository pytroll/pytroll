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

"""Behold the mighty datacenter.
"""

import socket, traceback
import time
import zmq
import threading
import Queue
import uuid
import getpass

from posttroll.message_broadcaster import sendaddress

from dc.publisher import Publisher

UID = uuid.uuid5(uuid.NAMESPACE_DNS, getpass.getuser()+"@"+socket.gethostname())

MESSAGE_PORT = 21201
PUBLISHER_PORT = 21202

def get_own_ip():
    """Get the host's ip number.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('smhi.se', 0))
    ip_ = sock.getsockname()[0]
    sock.close()
    return ip_

publisher = Publisher("tcp://eth0:%d"%PUBLISHER_PORT)

def process_message(msg):
    """Dummy processing function.
    """
    print "I'm processing a message: ", msg
    publisher.send(msg)

class Receiver(object):
    """Receive messages and process them.
    """
    def __init__(self, process_fun, port):
        self.fun = process_fun
        self.recv_thread = threading.Thread(target=self.loop_recv)
        self.fun_thread = threading.Thread(target=self.loop_fun)
        self.loop = True
        self.port = port
        self.socket = zmq.Context().socket(zmq.PULL)
        self.socket.bind('tcp://'+get_own_ip()+':'+str(self.port))
        self.message_queue = Queue.Queue()
        
    def loop_recv(self):
        """Message receiver loop.
        """
        while self.loop:
            # This is blocking, so don't forget to send a message when
            # self.loop becomes false !
            message = self.socket.recv()
            self.message_queue.put(message)

    def loop_fun(self):
        """Message processing loop.
        """
        while self.loop:
            # This is blocking, so don't forget to send a message when
            # self.loop becomes false !
            message = self.message_queue.get()
            self.fun(message)
                
    def start(self):
        """Start the datacenter.
        """
        self.recv_thread.start()
        self.fun_thread.start()

    def stop(self):
        """Stop the datacenter.
        """
        self.loop = False
        # Send a message to unblock the reciever socket.
        sock = zmq.Context().socket(zmq.PUSH)
        sock.connect('tcp://'+get_own_ip()+':'+str(self.port))
        sock.send("Exiting data center")


if __name__ == '__main__':
    BROADCASTER = sendaddress('dc', (get_own_ip(), MESSAGE_PORT), 2).start()
    MESSAGE_RECEIVER = Receiver(process_message, MESSAGE_PORT)
    MESSAGE_RECEIVER.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print "Exiting..."
        BROADCASTER.stop()
        MESSAGE_RECEIVER.stop()
    except:
        traceback.print_exc()


