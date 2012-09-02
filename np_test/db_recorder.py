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

"""Records new files into the database system.
"""

# TODO: remove old hanging subscriptions


from posttroll.subscriber import Subscriber
from db.pytroll_db import DCManager
from db.hl_file import File
from pyorbital.orbital import Orbital
from datetime import datetime, timedelta

from sqlalchemy.orm.exc import NoResultFound
import np.nameclient as nc
from threading import Thread

import logging
from logger import ColoredFormatter

LOG = logging.getLogger("db_recorder")
LOG.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = ColoredFormatter("[%(asctime)s %(levelname)-19s] %(message)s")
ch.setFormatter(formatter)
LOG.addHandler(ch)


sat_lookup = {"NPP": "SUOMI NPP",
              }

class DBRecorder(object):

    """The logging machine.

    Contains a thread listening to incomming messages, and a thread logging.
    """

    def __init__(self,
                 (nameserver_address, nameserver_port)=("localhost", 16543)):
        self.subscriber = Subscriber([], [])
        address = "tcp://"+nameserver_address+":"+str(nameserver_port)
        self.listener = Subscriber([address], [])
        self.listener_thread = Thread(target=self.listen)
        self.db_thread = Thread(target=self.record)
        self.dbm = None
        self.loop = True

    def start(self):
        """Starts the logging.
        """
        self.dbm = DCManager('postgresql://polar:polar@localhost:5432/sat_db')
        self.listener_thread.start()
        self.db_thread.start()
        
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

    def record(self):
        """Log stuff.
        """
        for msg in self.subscriber.recv(1):
            if msg:
                if msg.type == "file":
                    try:
                        file_obj = File(msg.data["filename"], self.dbm,
                                        filetype=msg.data.get("type", None),
                                        fileformat=msg.data.get("format", None))
                    except NoResultFound:
                        LOG.warning("Cannot process: " + str(msg))
                        continue
                    for key, val in msg.data.items():
                        if key == "filename":
                            continue
                        if key == "uri":
                            file_obj["URIs"] += [val]
                            continue
                        try:
                            file_obj[key] = val
                        except NoResultFound:
                            LOG.warning("Cannot add: " + str((key, val)))

                    LOG.debug("adding :" + str(msg))


                    # compute sub_satellite_track
                    satname = msg.data["satellite"]
                    sat = Orbital(sat_lookup.get(satname, satname))
                    dt_ = timedelta(seconds=10)
                    current_time = msg.data["start_time"] 
                    lonlat_list = []
                    while current_time <= msg.data["end_time"]:
                        pos = sat.get_lonlatalt(current_time)
                        lonlat_list.append(pos[:2])
                        current_time += dt_

                    LOG.debug("Computed sub-satellite track")
                
                    file_obj["sub_satellite_track"] = lonlat_list

                    LOG.debug("Added sub-satellite track")
                
            if not self.loop:
                LOG.info("Stop recording")
                break
    
    def stop(self):
        """Stop the machine.
        """
        self.loop = False

if __name__ == '__main__':
    import time
    try:
        recorder = DBRecorder()
        recorder.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        recorder.stop()
        print "Thanks for using pytroll/db_recorder. See you soon on www.pytroll.org!"
