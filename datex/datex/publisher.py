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
"""publisher.py, used by datex_server.

   Check for new files for a giver datatype and publish.
"""
#
# A proccess to check for new pol_L0 files and publish.
#
import copy
import os
from datetime import timedelta
from threading import Thread

import time
import zmq
from datex.config import DatexLastStamp
from datex.services import _get_file_list

from datex import logger, datex_config
from posttroll.message import Message

TIME_WAKEUP = 5
TIME_EPSILON = timedelta(microseconds=10)
#-----------------------------------------------------------------------------
#
# Process manager for the Publisher.
#
#-----------------------------------------------------------------------------
class Publisher(object):
    """The publisher class.
    """
    def __init__(self, *args, hearbeat=True):
        try:
            self.publish
        except AttributeError:
            raise AttributeError, ("You need to bind Publisher class before "
                                   "instantiating")
        self._process = Thread(target=check_and_publish,
                               args=args+(self.publish, heartbeat))

    @classmethod
    def bind(cls, destination):
        """Bind the publisher class to a port.
        """
        cls.destination = destination
        logger.info(cls.destination)
        cls.context = zmq.Context()
        cls.publish = cls.context.socket(zmq.PUB)
        cls.publish.bind(cls.destination)
    
    def start(self):
        """Start the publisher.
        """
        self._process.daemon = True # terminate when parent terminate
        self._process.start()
        return self

    def stop(self):
        """Stop the publisher (actually a dummy function).
        """
        return self

    def is_running(self):
        """Tell if the publisher is running.
        """
        return self._process.is_alive()

#-----------------------------------------------------------------------------
#
# In the child process.
#
#-----------------------------------------------------------------------------
def check_and_publish(datatype, rpc_metadata, publish, heartbeat):
    """Check for new files of type *datatype*, with the given *rpc_metadata*
    and publish them through *publish*.
    """
    stamp_config = DatexLastStamp(datatype)

    def younger_than_stamp_files():
        """Uses glob polling to get new files.
        """
        fdir, fglob = datex_config.get_path(datatype)
        del fglob
        fstamp = stamp_config.get_last_stamp()
        for fname, ftime in _get_file_list(datatype,
                                       time_start=fstamp + TIME_EPSILON):
            if datex_config.distribute(datatype):
                yield os.path.join(fdir, fname)
            stamp_config.update_last_stamp(ftime)

    # Give the publisher a little time to initialize
    # (e.g reconnections from subscribers)
    time.sleep(1)
    logger.info('publisher starting')
    try:
        while(True):
            if heartbeat:
                msg = Message('/hearbeat', 'heartbeat', str(datetime.utcnow()))
                logger.info('sending: ' + str(msg))
                try:
                    publish.send(str(msg))
                except zmq.ZMQError:
                    logger.exception('publish failed')
            for filedesc in younger_than_stamp_files():
                # Publish new files
                data = copy.copy(rpc_metadata)
                data['uri'] += os.path.basename(filedesc)
                msg = Message('/' + datatype, 'file', data)
                logger.info('sending: ' + str(msg))
                try:
                    publish.send(str(msg))
                except zmq.ZMQError:
                    logger.exception('publish failed')
            time.sleep(TIME_WAKEUP)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        logger.info('publisher stopping')
        publish.close()
