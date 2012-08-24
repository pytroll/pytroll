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
from ConfigParser import ConfigParser, NoOptionError
from zmq import Context, Poller, LINGER, PUB, REP, REQ, POLLIN, NOBLOCK
from posttroll.message import Message
from posttroll import strp_isoformat
from posttroll.subscriber import Subscriber

from urlparse import urlparse, urlunparse
from threading import Thread, Lock
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

class Holder(object):

    def __init__(self, configfile):
        self._holder = {}
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
        self._lock = Lock()
        
    def __del__(self, *args, **kwargs):
        self._socket.close()

    def get(self, *args, **kwargs):
        return self._holder.get(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self._holder.__getitem__(*args, **kwargs)
    
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
        self._lock.acquire()
        try:
            if(satellite not in self._holder or
               utctime not in self._holder[satellite]):
                self._holder.setdefault(satellite,
                                        {})[utctime] = (line_start,
                                                        filename,
                                                        elevation)
                self.send_have(satellite, utctime, elevation)
        finally:
            self._lock.release()
        

class FileStreamer(ProcessEvent):
    """Get the updates from files.

    TODO: separate holder from file handling.
    """
    def __init__(self, holder, *args, **kwargs):
        ProcessEvent.__init__(self, *args, **kwargs)
        self._file = None
        self._filename = ""
        self._where = 0
        self._satellite = ""

        self.scanlines = holder

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
            if all(abs(np.array((644, 367, 860, 413, 527, 149)) - 
                       array["frame_sync"]) > 1):
                array = array.newbyteorder()
            year = int(os.path.split(event.pathname)[1][:4])
            utctime = datetime(year, 1, 1) + timecode(array["timecode"][0])
            print "Got line", utctime, self._satellite

            # FIXME: get real elevation
            elevation = uniform(5, 90)
            # TODO:
            # - serve also already present files
            self.scanlines.add_scanline(self._satellite, utctime,
                                        elevation, line_start, self._filename)

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


class MirrorStreamer(Thread):
    """Act as a relay...
    """

    def __init__(self, holder, configfile):
        Thread.__init__(self)
        
        self.scanlines = holder
        
        cfg = ConfigParser()
        cfg.read(configfile)
        host = cfg.get("local_reception", "mirror")
        hostname = cfg.get(host, "hostname")
        port = cfg.get(host, "pubport")
        rport = cfg.get(host, "reqport")
        address = "tcp://" + hostname + ":" + port
        self._sub = Subscriber([address], "hrpt 0")
        self._reqaddr = "tcp://" + hostname + ":" + rport

    def run(self):

        for message in self._sub.recv(1):
            if message is None:
                continue
            if(message.type == "have"):
                self.scanlines.add_scanline(message.data["satellite"],
                                            strp_isoformat(message.data["timecode"]),
                                            message.data["elevation"],
                                            None,
                                            self._reqaddr)
    def stop(self):
        """Stop streaming.
        """
        self._sub.stop()
        
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

        self.mirrors = {}


    def __del__(self, *args, **kwargs):
        self._socket.close()
        for mirror in self.mirrors.values():
            mirror.close()
            
        
    def forward_request(self, address, message):
        """Forward a request to another server.
        """
        if address not in self.mirrors:
            context = Context()
            socket = context.socket(REQ)
            socket.setsockopt(LINGER, 1)
            socket.connect(address)
            self.mirrors[address] = socket
        else:
            socket = self.mirrors[address]
        socket.send(str(message))
        return socket.recv()


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
                    print self._holder.get(sat, [])
                    resp = Message('/oper/polar/direct_readout/' + self._station,
                                   "scanlines",
                                   [(utctime.isoformat(),
                                     self._holder[sat][utctime][2])
                                    for utctime in self._holder.get(sat, [])
                                    if utctime >= start_time
                                    and utctime <= end_time])
                    self._socket.send(str(resp))

                # send one scanline
                elif(message.type == "request" and
                     message.data.startswith("scanline")):
                    sat = message.data.split(" ")[1]
                    utctime = strp_isoformat(message.data.split(" ")[2])
                    url = urlparse(self._holder[sat][utctime][1])
                    if url.scheme in ["", "file"]: # data is locally stored.
                        with open(url.path, "rb") as fp_:
                            fp_.seek(self._holder[sat][utctime][0])
                            resp = Message('/oper/polar/direct_readout/'
                                           + self._station,
                                           "scanline",
                                           fp_.read(LINE_SIZE),
                                           binary=True)
                    else: # it's the address of a remote server.
                        resp = self.forward_request(urlunparse(url),
                                                    message)
                    self._socket.send(str(resp))

                # take in a new scanline
                elif(message.type == "notice" and
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

    wm_ = WatchManager()
    mask = IN_CREATE | IN_OPEN | IN_CLOSE_WRITE | IN_MODIFY

    scanlines = Holder(configfile)
    fstreamer = FileStreamer(scanlines)
    notifier = Notifier(wm_, fstreamer)
    cfg = ConfigParser()
    cfg.read(configfile)
    path = cfg.get("local_reception", "data_dir")
    wm_.add_watch(path, mask, rec=False)

    local_station = cfg.get("local_reception", "localhost")
    responder_port = cfg.get(local_station, "reqport")
    responder = Responder(scanlines, configfile,
                          "tcp://*:" + responder_port, REP)
    responder.start()

    mirror = None
    try:
        mirror = MirrorStreamer(scanlines, configfile)
        mirror.start()
    except NoOptionError:
        pass
    
    notifier.loop()
    responder.stop()
    if mirror is not None:
        mirror.stop()
        
    print "Thanks for using pytroll/trollcast. See you soon on www.pytroll.org!"

if __name__ == '__main__':
    import sys

    main(sys.argv[1])
