#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012 SMHI

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

"""Trollcast, server side.

Trollcasting is loosely based on the bittorrent concepts, and adapted to
satellite data.

Limitations:
 - HRPT specific at the moment

TODO:
 - Include files from a library, not only the currently written file to the
   list of scanlines
 - Implement choking
 - de-hardcode filename
"""
from __future__ import with_statement 

from pyinotify import (ProcessEvent, Notifier, WatchManager,
                       IN_OPEN, IN_MODIFY, IN_CREATE, IN_CLOSE_WRITE)
from ConfigParser import ConfigParser
from zmq import Context, Poller, PUB, REP, POLLIN, NOBLOCK
from posttroll.message import Message, strp_isoformat
from threading import Thread
import numpy as np
import os
from datetime import datetime, timedelta
from random import uniform

LINE_SIZE = 11090 * 2

def timecode(tc_array):
    word = tc_array[0]
    day = word
    word = tc_array[1]
    msecs = ((127) & word) * 1024
    word = tc_array[2]
    msecs += word & 1023
    msecs *= 1024
    word = tc_array[3]
    msecs += word & 1023
    # FIXME : should return current year !
    return timedelta(days=int(day/2 - 1), milliseconds=int(msecs))

class FileStreamer(ProcessEvent):
    
    def __init__(self, holder, configfile, *args, **kwargs):
        ProcessEvent.__init__(self, *args, **kwargs)
        self._file = None
        self._filename = ""
        self._where = 0
        self._satellite = ""

        cfg = ConfigParser()
        cfg.read(configfile)
        host = cfg.get("local_reception", "localhost")
        hostname = cfg.get(host, "hostname")
        port = cfg.get(host, "pubport")
        self._addr = hostname + ":" + port

        self._station = cfg.get("local_reception", "station")

        self._context = Context()
        self._socket = self._context.socket(PUB)
        self._socket.bind("tcp://*:" + port)
        self.scanlines = holder

    def get(self, *args, **kwargs):
        return self.scanlines.get(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self.scanlines.__getitem__(*args, **kwargs)

    def __del__(self, *args, **kwargs):
        self._socket.close()

    def process_IN_CREATE(self, event):
        print "Creating:", event.pathname

    def process_IN_OPEN(self, event):
        if self._file is None and event.pathname.endswith(".temp"):
            print "Opening:", event.pathname
            self._filename = event.pathname
            self._file = open(event.pathname, "rb")
            self._where = 0
            self._satellite = "".join(event.pathname.split("_")[1:3])[:-5]

    def process_IN_MODIFY(self, event):
        self.process_IN_OPEN(event)

        if event.pathname != self._filename:
            return
            
        self._file.seek(self._where)
        line = self._file.read(LINE_SIZE)
        while len(line) == LINE_SIZE:
            line_start = self._where
            self._where = self._file.tell()
            dtype = np.dtype([('frame_sync', '>u2', (6, )),
                              ('id', [('id', '>u2'),
                                      ('spare', '>u2')]),
                              ('timecode', '>u2', (4, )),
                              ('telemetry', [("ramp_calibration", '>u2', (5, )),
                                             ("PRT", '>u2', (3, )),
                                             ("ch3_patch_temp", '>u2'),
                                             ("spare", '>u2'),]),
                              ('back_scan', '>u2', (10, 3)),
                              ('space_data', '>u2', (10, 5)),
                              ('sync', '>u2'),
                              ('TIP_data', '>u2', (520, )),
                              ('spare', '>u2', (127, )),
                              ('image_data', '>u2', (2048, 5)),
                              ('aux_sync', '>u2', (100, ))])


            array = np.fromstring(line, dtype=dtype)
            if not np.allclose(np.array((644, 367, 860, 413, 527, 149)),
                               array["frame_sync"]):
                array = array.newbyteorder()
            year = int(os.path.split(event.pathname)[1][:4])
            utctime = datetime(year, 1, 1) + timecode(array["timecode"][0])
            print "Got line", utctime, self._satellite

            # TODO:
            # - serve also already present files
            self.scanlines.setdefault(self._satellite, {})[utctime] = \
                                                       (line_start,
                                                        self._filename)
            # FIXME: get real elevation
            self.send_have(self._satellite, utctime, uniform(5, 90))

            line = self._file.read(LINE_SIZE)

        self._file.seek(self._where)        

    def process_IN_CLOSE_WRITE(self, event):
        if event.pathname == self._filename:
            print "Closing:", event.pathname
            self._file.close()
            self._file = None
            self._filename = ""
            self._where = 0
            self._satellite = ""

    def send_have(self, satellite, utctime, elevation):
        """Sends 'have' message for *satellite*, *utctime*, *elevation*.
        """
        to_send = {}
        to_send["satellite"] = satellite
        to_send["timecode"] = utctime.isoformat()
        to_send["elevation"] = elevation
        to_send["origin"] = self._addr
        msg = Message('/oper/polar/direct_readout/' + self._station, "have",
                      to_send).encode()
        self._socket.send(msg)

    def add_scanline(self, satellite, utctime, elevation, line_start, filename):
        """Adds the scanline to the server. Typically used by the client to
        signal newly received lines.
        """
        if(satellite not in self.scanlines or
           utctime not in self.scanlines[satellite]):
            self.scanlines.setdefault(satellite,
                                      {})[utctime] = (line_start,
                                                      filename)
            self.send_have(satellite, utctime, elevation)

class Looper(object):

    def __init__(self):
        self._loop = True

    def stop(self):
        self._loop = False

class Socket(object):
    def __init__(self, addr, stype):
        self._context = Context()
        self._socket = self._context.socket(stype)
        if stype in [REP, PUB]:
            self._socket.bind(addr)
        else:
            self._socket.connect(addr)

    def __del__(self, *args, **kwargs):
        self._socket.close()

class SocketLooper(Socket, Looper):
    
    def __init__(self, *args, **kwargs):
        Looper.__init__(self)
        Socket.__init__(self, *args, **kwargs)

class SocketLooperThread(SocketLooper, Thread):
    def __init__(self, *args, **kwargs):
        Thread.__init__(self)
        SocketLooper.__init__(self, *args, **kwargs)

class Responder(SocketLooperThread):

    # TODO: this should not respond to everyone. It should check if the
    # requester is listed in the configuration file...
    
    def __init__(self, holder, configfile, *args, **kwargs):
        SocketLooperThread.__init__(self, *args, **kwargs)
        self._holder = holder
        self._loop = True

        cfg = ConfigParser()
        cfg.read(configfile)
        self._station = cfg.get("local_reception", "station")
        
    def __del__(self, *args, **kwargs):
        self._socket.close()
        
    def run(self):
        poller = Poller()
        poller.register(self._socket, POLLIN)
        
        while self._loop:
            socks = dict(poller.poll(timeout=2))
            if self._socket in socks and socks[self._socket] == POLLIN:
                message = Message(rawstr=self._socket.recv(NOBLOCK))
                
                # send list of scanlines
                if(message.type == "request" and
                   message.data.startswith("scanlines")):
                    elts = message.data.split(" ")
                    sat = elts[1]
                    if len(elts) > 2:
                        start_time = strp_isoformat(elts[2])
                    else:
                        start_time = datetime(1950, 1, 1)
                    if len(elts) > 3:
                        end_time = strp_isoformat(elts[3])
                    else:
                        end_time = datetime(19500, 1, 1)
                    resp = Message('/oper/polar/direct_readout/' + self._station,
                                   "scanlines",
                                   [utctime.isoformat()
                                    for utctime in self._holder.get(sat, [])
                                    if utctime >= start_time
                                    and utctime <= end_time])
                    self._socket.send(str(resp))

                # send one scanline
                if(message.type == "request" and
                   message.data.startswith("scanline")):
                    sat = message.data.split(" ")[1]
                    utctime = strp_isoformat(message.data.split(" ")[2])
                    with open(self._holder[sat][utctime][1], "rb") as fp_:
                        fp_.seek(self._holder[sat][utctime][0])
                        resp = Message('/oper/polar/direct_readout/'
                                       + self._station,
                                       "scanline",
                                       fp_.read(LINE_SIZE),
                                       binary=True)
                    self._socket.send(str(resp))

                # take in a new scanline
                if(message.type == "notice" and
                   message.data.startswith("scanline")):
                    sat, utctime, elevation, filename, line_start = \
                         message.data.split(' ')[1:]
                    utctime = strp_isoformat(utctime)
                    self._holder.add_scanline(sat, utctime, float(elevation),
                                              int(line_start), filename)
                    resp = Message('/oper/polar/direct_readout/'
                                       + self._station,
                                       "notice",
                                       "ack")
                    self._socket.send(str(resp))
                
    def stop(self):
        self._loop = False


def main(configfile):
    """Serve forever.
    """
    scanlines = {}

    wm_ = WatchManager()
    mask = IN_CREATE | IN_OPEN | IN_CLOSE_WRITE | IN_MODIFY

    handler = FileStreamer(scanlines, configfile)
    notifier = Notifier(wm_, handler)
    cfg = ConfigParser()
    cfg.read(configfile)
    path = cfg.get("local_reception", "data_dir")
    wm_.add_watch(path, mask, rec=False)

    local_station = cfg.get("local_reception", "localhost")
    responder_port = cfg.get(local_station, "reqport")
    responder = Responder(handler, configfile, "tcp://*:" + responder_port, REP)
    responder.start()
    
    notifier.loop()
    responder.stop()
    print "Thanks for using pytroll/trollcast. See you soon on www.pytroll.org!"

if __name__ == '__main__':
    import sys

    main(sys.argv[1])
