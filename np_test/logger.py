#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Logger for pytroll system.
"""


# TODO: remove old hanging subscriptions

import zmq
from posttroll.subscriber import Subscriber
from posttroll.message import Message
import np.nameclient as nc
from threading import Thread

import logging


class PytrollFormatter(logging.Formatter):
    """Formats a pytroll message inside a log record.
    """
    
    def __init__(self, subject):
        logging.Formatter.__init__(self)
        self._subject = subject

    def format(self, record):
        mesg = Message(self._subject, str(record.levelname).lower(),
                       record.getMessage())
        return str(mesg)

class PytrollHandler(logging.Handler):
    """Sends the record through a pytroll publisher.
    """

    def __init__(self, publisher):
        logging.Handler.__init__(self)
        self._publisher = publisher

    def emit(self, record):
        message = self.format(record)
        self._publisher.send(message)



BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
    'WARNING': YELLOW,
    'INFO': GREEN,
    'DEBUG': BLUE,
    'CRITICAL': MAGENTA,
    'ERROR': RED
}

COLOR_SEQ = "\033[1;%dm"
RESET_SEQ = "\033[0m"

class ColoredFormatter(logging.Formatter):
    """Adds a color for the levelname.
    """
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = (COLOR_SEQ % (30 + COLORS[levelname])
                               + levelname + RESET_SEQ)
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)



#logging.basicConfig(format='[%(asctime)s %(levelname)s] %(message)s',
#                    level=logging.DEBUG)

LOG = logging.getLogger("pytroll")
LOG.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = ColoredFormatter("[%(asctime)s %(levelname)-19s] %(message)s")
ch.setFormatter(formatter)
LOG.addHandler(ch)

class Logger(object):

    """The logging machine.

    Contains a thread listening to incomming messages, and a thread logging.
    """

    def __init__(self,
                 (nameserver_address, nameserver_port)=("localhost", 16543)):
        self.subscriber = Subscriber([], [])
        address = "tcp://"+nameserver_address+":"+str(nameserver_port)
        self.listener = Subscriber([address], [])
        self.listener_thread = Thread(target=self.listen)
        self.log_thread = Thread(target=self.log)
        self.loop = True

    def start(self):
        """Starts the logging.
        """
        self.listener_thread.start()
        self.log_thread.start()
        
    def listen(self):
        """Listen to incomming messages.
        """
        for addr in nc.get_address(""):
            LOG.info("Listening to " + str(addr["URI"]) +
                         " (" + str(addr["type"]) + ")")
            self.subscriber.add(addr["URI"], addr["type"])
        
        for msg in self.listener.recv(1):
            if msg:
                LOG.info("Now listening to " + str(msg.data["URI"]) +
                             " (" + str(msg.data["type"]) + ")")
                # add new address to subscriber
                self.subscriber.add(msg.data["URI"], msg.data["type"])
            if not self.loop:
                break
        LOG.info("Stop listening")

    def log(self):
        """Log stuff.
        """
        for msg in self.subscriber.recv(1):
            if msg:
                if msg.type in ["debug", "info",
                                "warning", "error",
                                "critical"]:
                    getattr(LOG, msg.type)(msg.subject + " " +
                              msg.sender + " " +
                              str(msg.data) + " " +
                              str(msg.time))
                    
                elif msg.binary:
                    LOG.debug(msg.subject + " " +
                              msg.sender + " " +
                              msg.type + " " +
                              "[binary] " +
                              str(msg.time))
                else:
                    LOG.debug(msg.subject + " " +
                              msg.sender + " " +
                              msg.type + " " +
                              str(msg.data) + " " +
                              str(msg.time))
            if not self.loop:
                LOG.info("Stop logging")
                break
    
    def stop(self):
        """Stop the machine.
        """
        self.loop = False

if __name__ == '__main__':
    import time
    try:
        logger = Logger()
        logger.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.stop()
        print "Thanks for using pytroll/logger. See you soon on www.pytroll.org!"
