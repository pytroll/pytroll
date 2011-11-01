#
# Copyright (c) 2009.
#
# DMI
# Lyngbyvej 100
# DK-2100 Copenhagen
# Denmark
#
# Author(s): 
#   Lars Orum Rasmussen
#   Martin Raspaud

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""A subscriber. Listen for new files of a give type.
"""
import zmq

from posttroll.message import Message
from datex import logger

context = zmq.Context() 
class Subscriber(object):
    """A class to subscribe to a given subject and wait for messages.
    """
    def __init__(self, subject, address):
        subscriber = context.socket(zmq.SUB)
        if subject:
            logger.info("Subscribing to '%s'"%subject)
            subscriber.setsockopt(zmq.SUBSCRIBE, subject)
            # corresponding heartbeat
            sub = subject.split()[0].split('://')
            heartbeat_subject = sub[0] + "://hearbeat/" + sub[1] + ' heartbeat'
        else:
            heartbeat_subject = "pytroll://hearbeat"
        # subscribe for heartbeats
        logger.info("Subscribing to '%s'"%heartbeat_subject)
        subscriber.setsockopt(zmq.SUBSCRIBE, heartbeat_subject)
        self.subscriber = subscriber
        self.destination = address
        logger.info("Destination '%s'"%self.destination)

    def __call__(self):
        return self.get()

    def get(self, timeout=None):
        """Return a published message or None if a timeout has happend.
        """
        if timeout:
            timeout *= 1000.
        self.subscriber.connect(self.destination)
        poller = zmq.Poller()
        poller.register(self.subscriber, zmq.POLLIN)
        try:
            while(True):
                try:
                    ret = poller.poll(timeout=timeout)
                    if ret:
                        if ret[0][0] == self.subscriber:
                            msg = Message.decode(
                                self.subscriber.recv(zmq.NOBLOCK))
                            yield msg
                        else:
                            logger.error("WHAT THE HECK")
                    else:
                        # timeout
                        yield None
                except zmq.ZMQError:
                    logger.exception('recv failed')
        finally:
            poller.unregister(self.subscriber)
            self.subscriber.close()        
