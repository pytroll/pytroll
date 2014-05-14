#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, 2013 Martin Raspaud

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
from ConfigParser import ConfigParser

import logging
LOG = logging.getLogger(__name__)

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
        
    def start(self):
        """Starts the logging.
        """
        config = ConfigParser()
        config.read(self._config_file)
        mode = config.get("default", "mode")
        self.dbm = DCManager(config.get(mode, "uri"))
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

    def insert_line(self, msg):
        """Insert the line corresponding to *msg* in the database.
        """
        if msg.type == "file":
            required_fields = ["start_time", "end_time"]

            for field in required_fields:
                if field not in msg.data.keys():
                    LOG.warning("Missing required " + field
                                + ", not creating record from "
                                + str(msg))
                    return

            try:
                file_obj = File(msg.data["filename"], self.dbm,
                                filetype=msg.data.get("type", None),
                                fileformat=msg.data.get("format", None))
            except NoResultFound:
                LOG.warning("Cannot process: " + str(msg))
                return
            
            LOG.debug("adding :" + str(msg))

            for key, val in msg.data.items():
                if key in ["filename", "type"]:
                    continue
                if key == "uri":
                    file_obj["URIs"] += [val]
                    continue
                try:
                    file_obj[key] = val
                except NoResultFound:
                    LOG.warning("Cannot add: " + str((key, val)))


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


    def record(self):
        """Log stuff.
        """
        for msg in self.subscriber.recv(1):
            if msg:
                self.insert_line(msg)
            if not self.loop:
                LOG.info("Stop recording")
                break
    
    def stop(self):
        """Stop the machine.
        """
        self.loop = False

if __name__ == '__main__':
    import time
    from logger import ColoredFormatter

    LOG = logging.getLogger("db_recorder")
    LOG.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = ColoredFormatter("[%(asctime)s %(levelname)-19s] %(message)s")
    ch.setFormatter(formatter)
    LOG.addHandler(ch)

    try:
        recorder = DBRecorder()
        recorder.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        recorder.stop()
        print "Thanks for using pytroll/db_recorder. See you soon on www.pytroll.org!"


### insert a line

# pytroll://oper/polar/direct_readout/norrköping file safusr.u@lxserv248.smhi.se 2013-01-15T14:19:19.135161 {u'satellite': u'NOAA 15', u'format': u'HRPT', u'start_time': 2013-01-15T14:03:55, u'level': u'0', u'orbit_number': 76310, u'uri': u'ssh://pps.smhi.se//san1/polar_in/direct_readout/hrpt/20130115140355_NOAA_15.hmf', u'filename': u'20130115140355_NOAA_15.hmf', u'end_time': 2013-01-15T14:19:07), u'type': u'binary'} 

# from db_recorder import DBRecorder
# rec = DBRecorder()
# rec.start()


# mystr = """pytroll://oper/polar/direct_readout/norrköping file safusr.u@lxserv248.smhi.se 2013-01-15T14:19:19.135161 v1.01 application/json "{'satellite': 'NOAA 15', 'format': 'HRPT', 'start_time': datetime.datetime(2013, 1, 15, 14, 3, 55), 'level': '0', 'orbit_number': 76310, 'uri': 'ssh://pps.smhi.se//san1/polar_in/direct_readout/hrpt/20130115140355_NOAA_15.hmf', 'filename': '20130115140355_NOAA_15.hmf', 'end_time': datetime.datetime(2013, 1, 15, 14, 19, 7), 'type': 'binary'}" """

# from posttroll.message import Message
# m = Message(rawstr=mystr)
# m.data = eval(m.data)

# rec.insert_line(m)
