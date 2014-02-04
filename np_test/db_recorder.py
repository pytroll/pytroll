#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, 2013, 2014 Martin Raspaud

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
from pyresample.utils import get_area_def
from sqlalchemy.orm.exc import NoResultFound
import np.nameclient as nc
from threading import Thread
from ConfigParser import ConfigParser

import logging
logger = logging.getLogger(__name__)

sat_lookup = {"NPP": "SUOMI NPP",
              }

class DBRecorder(object):

    """The database recording machine.

    Contains a thread listening to incomming messages, and a thread recording
    to the database.
    """

    def __init__(self,
                 (nameserver_address, nameserver_port)=("localhost", 16543),
                 config_file="db.cfg"):
        self.subscriber = Subscriber([], [])
        address = "tcp://"+nameserver_address+":"+str(nameserver_port)
        self.listener = Subscriber([address], [])
        self.listener_thread = Thread(target=self.listen)
        self.db_thread = Thread(target=self.record)
        self.dbm = None
        self.loop = True
        self._config_file = config_file
        
    def init_db(self):
        config = ConfigParser()
        config.read(self._config_file)
        mode = config.get("default", "mode")
        self.dbm = DCManager(config.get(mode, "uri"))

    def start(self):
        """Starts the logging.
        """
        self.init_db()
        self.listener_thread.start()
        self.db_thread.start()
        
    def listen(self):
        """Listen to incomming messages.
        """
        try:
            for addr in nc.get_address(""):
                logger.info("Listening to " + str(addr["URI"]) +
                             " (" + str(addr["type"]) + ")")
                self.subscriber.add(addr["URI"], addr["type"])

            for msg in self.listener.recv(1):
                if msg:
                    logger.info("Now listening to " + str(msg.data["URI"]) +
                                 " (" + str(msg.data["type"]) + ")")
                    # add new address to subscriber
                    self.subscriber.add(msg.data["URI"], msg.data["type"])
                if not self.loop:
                    break
        except:
            logger.exception("Something wrong happened in listener")
            raise
        logger.info("Stop listening")

    def insert_line(self, msg):
        """Insert the line corresponding to *msg* in the database.
        """
        if msg.type == "file":

            if (("start_time" not in msg.data.keys() or
                 "end_time" not in msg.data.keys()) and
                "area" not in msg.data.keys()):
                logger.warning("Missing field, not creating record from "
                            + str(msg))
                return
            #required_fields = ["start_time", "end_time"]
            # for field in required_fields:
            #     if field not in msg.data.keys():
            #         logger.warning("Missing required " + field
            #                     + ", not creating record from "
            #                     + str(msg))
            #         return

            try:
                file_obj = File(msg.data["filename"], self.dbm,
                                filetype=msg.data.get("type", None),
                                fileformat=msg.data.get("format", None))
            except NoResultFound:
                logger.warning("Cannot process: " + str(msg))
                return
            
            logger.debug("adding :" + str(msg))

            for key, val in msg.data.items():
                if key in ["filename", "type", "area"]:
                    continue
                if key == "uri":
                    file_obj["URIs"] += [val]
                    continue
                try:
                    file_obj[key] = val
                except NoResultFound:
                    logger.warning("Cannot add: " + str((key, val)))


            if ("start_time" in msg.data.keys() and
                "end_time" in msg.data.keys()):
                # compute sub_satellite_track
                satname = msg.data["satellite"]
                sat = Orbital(sat_lookup.get(satname, satname))
                dt_ = timedelta(seconds=10)
                current_time = msg.data["start_time"] 
                lonlat_list = []
                while current_time < msg.data["end_time"]:
                    pos = sat.get_lonlatalt(current_time)
                    lonlat_list.append(pos[:2])
                    current_time += dt_
                pos = sat.get_lonlatalt(msg.data["end_time"])
                lonlat_list.append(pos[:2])

                logger.debug("Computed sub-satellite track")

                if len(lonlat_list) < 2:
                    logger.info("Sub satellite track to short, skipping it.")
                else:
                    file_obj["sub_satellite_track"] = lonlat_list
                    logger.debug("Added sub-satellite track")

            if "area" in msg.data.keys():
                logger.debug("Add area definition to the data")
                area_def = get_area_def(str(msg.data["area"]["id"]),
                                        str(msg.data["area"]["name"]),
                                        str(msg.data["area"]["proj_id"]),
                                        str(msg.data["area"]["proj4"]),
                                        msg.data["area"]["shape"][0],
                                        msg.data["area"]["shape"][1],
                                        msg.data["area"]["area_extent"])
                logger.debug("Adding boundary...")
                file_obj["area"] = area_def
                logger.debug("Boundary added.")


    def record(self):
        """Log stuff.
        """
        try:
            for msg in self.subscriber.recv(1):
                if msg:
                    self.insert_line(msg)
                if not self.loop:
                    logger.info("Stop recording")
                    break
        except:
            logger.exception("Something went wrong in record")
            raise
    
    def stop(self):
        """Stop the machine.
        """
        self.loop = False

if __name__ == '__main__':
    import time
    from logger import ColoredFormatter

    logger = logging.getLogger("db_recorder")
    logger.setLevel(logging.DEBUG)

    #ch = logging.StreamHandler()
    ch = logging.handlers.TimedRotatingFileHandler(
        "/var/log/satellit/db_recorder.log",
        'midnight', backupCount=30, utc=True)
    ch.setLevel(logging.DEBUG)

    formatter = ColoredFormatter("[%(asctime)s %(name)s %(levelname)-19s] %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    try:
        recorder = DBRecorder()
        recorder.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        recorder.stop()
        print "Thanks for using pytroll/db_recorder. See you soon on www.pytroll.org!"



