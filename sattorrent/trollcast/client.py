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

"""Trollcast client. Leeches all it can :)
"""
from __future__ import with_statement 

from ConfigParser import ConfigParser
from posttroll.subscriber import Subscriber
from posttroll.message import Message, strp_isoformat
from zmq import Context, REQ, LINGER, Poller, POLLIN
from threading import Thread, Timer
import numpy as np
from Queue import Queue, Empty
from datetime import timedelta, datetime
import logging

logger = logging.getLogger(__name__)

# TODO: what if a scanline never arrives ? do we wait for it forever ?

# FIXME: this should be configurable depending on the type of data.
LINES_PER_SECOND = 6
LINE_SIZE = 11090 * 2
CLIENT_TIMEOUT = timedelta(seconds=30)

BUFFER_TIME = 2.0

def create_subscriber(cfgfile):
    """Create a new subscriber for all the remote hosts in cfgfile.
    """

    cfg = ConfigParser()
    cfg.read(cfgfile)
    addrs = []
    for host in cfg.get("local_reception", "remotehosts").split():
        addrs.append("tcp://" +
                     cfg.get(host, "hostname") + ":" + cfg.get(host, "pubport"))
    localhost = cfg.get("local_reception", "localhost")
    addrs.append("tcp://" +
                 cfg.get(localhost, "hostname") + ":" +
                 cfg.get(localhost, "pubport"))
    logger.debug("Subscribing to " + str(addrs))
    return Subscriber(addrs, "hrpt 0", translate=True)


def create_requesters(cfgfile):
    """Create requesters to all the configure remote hosts.
    """
    cfg = ConfigParser()
    cfg.read(cfgfile)
    requesters = {}
    for host in cfg.get("local_reception", "remotehosts").split():
        host, port = (cfg.get(host, "hostname"),  cfg.get(host, "reqport"))
        requesters[host] = Requester(host, port)
    host = cfg.get("local_reception", "localhost")
    host, port = (cfg.get(host, "hostname"),  cfg.get(host, "reqport"))
    requesters[host] = Requester(host, port)
    return requesters

class Requester(object):

    """Make a request connection, waiting to get scanlines .
    """
    
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._context = Context()
        self._socket = self._context.socket(REQ)
        self._socket.setsockopt(LINGER, 1)
        self._socket.connect("tcp://"+host+":"+str(port))
        self._poller = Poller()
        self._poller.register(self._socket, POLLIN)

    def stop(self):
        """Close the socket.
        """
        self._socket.close()

    def __del__(self, *args, **kwargs):
        self.stop()

    def send(self, msg):
        """Send a message.
        """
        return self._socket.send(str(msg))

    def recv(self, timeout=None):
        """Receive a message. *timeout* in ms.
        """
        if self._poller.poll(timeout):
            return Message(rawstr=self._socket.recv())
        else:
            raise IOError("Timeout from " + str(self._host) +
                          ":" + str(self._port))
        
    def get_line(self, satellite, utctime):
        """Get the scanline of *satellite* at *utctime*.
        """
        msg = Message('/oper/polar/direct_readout/norrköping',
                      'request',
                      {"type": "scanline",
                       "satellite": satellite,
                       "utctime": utctime.isoformat()})
        self.send(msg)
        return self.recv(1000).data


    def get_slice(self, satellite, start_time, end_time):
        msg = Message('/oper/polar/direct_readout/norrköping',
                      'request',
                      {"type": 'scanlines',
                       "satellite": satellite,
                       "start_time": start_time.isoformat(),
                       "end_time": end_time.isoformat()})
        self.send(msg)
        return self.recv(1000).data

    def send_lineinfo(self, sat, utctime, elevation, filename, pos):
        """Send information to our own server.
        """

        msg = Message('/oper/polar/direct_readout/norrköping',
                      'notice',
                      {"type": 'scanline',
                       "satellite": sat,
                       "utctime": utctime.isoformat(),
                       "elevation": elevation,
                       "filename": filename,
                       "file_position": pos})
        self.send(msg)
        self._socket.recv()         

class HaveBuffer(Thread):
    """Listen to incomming have messages.
    """

    def __init__(self, cfgfile="sattorrent.cfg"):
        Thread.__init__(self)
        self._sub = create_subscriber(cfgfile)
        self.scanlines = {}
        self._queues = []

    def add_queue(self, queue):
        """Adds a queue to dispatch have messages to
        """
        self._queues.append(queue)

    def del_queue(self, queue):
        """Deletes a dispatch queue.
        """
        self._queues.remove(queue)

    def send_to_queues(self, sat, utctime):
        """Send scanline at *utctime* to queues.
        """

        for queue in self._queues:
            queue.put_nowait((sat, utctime, self.scanlines[sat][utctime]))
        

    def run(self):

        for message in self._sub.recv(1):
            if message is None:
                continue
            if(message.type == "have"):
                sat = message.data["satellite"]
                utctime = strp_isoformat(message.data["timecode"])
                # This should take care of address translation.
                sender = (message.sender.split("@")[1] + ":" +
                          message.data["origin"].split(":")[1])
                elevation = message.data["elevation"]
                
                self.scanlines.setdefault(sat, {})
                if utctime not in self.scanlines[sat]:
                    self.scanlines[sat][utctime] = [(sender, elevation)]
                    # TODO: This implies that we always wait BUFFER_TIME before
                    # sending to queue. In the case were the "have" messages of
                    # all servers were sent in less time, we should not be
                    # waiting...
                    Timer(BUFFER_TIME,
                          self.send_to_queues,
                          args=[sat, utctime]).start()
                else:
                    # Since append is atomic in CPython, this should work.
                    # However, if it is not, then this is not thread safe.
                    self.scanlines[sat][utctime].append((sender, elevation))
                
    def stop(self):
        self._sub.stop()

def compute_line_times(utctime, start_time, end_time):
    """Compute the times of lines if a swath order depending on a reference
    *utctime*.
    """
    offsets = (np.arange(0, 1, 1.0 / LINES_PER_SECOND) +
               utctime.microsecond / 1000000.0)
    offsets = offsets.round(3)
    offsets[offsets > 1] -= 1
    offsets -= start_time.microsecond
    offset = timedelta(seconds=min(abs(offsets)))
    time_diff = (end_time - start_time - offset)
    time_diff = time_diff.seconds + time_diff.microseconds / 1000000.0
    nblines = int(np.ceil(time_diff * LINES_PER_SECOND))
    rst = start_time + offset
    linepos = [rst + timedelta(seconds=round(i * 1.0/
                                             LINES_PER_SECOND, 3))
               for i in range(nblines)]
    linepos = set(linepos)
    return linepos

class Client(HaveBuffer):

    def __init__(self, cfgfile="sattorrent.cfg"):
        HaveBuffer.__init__(self, cfgfile)
        self._requesters = create_requesters(cfgfile)
        self.cfgfile = cfgfile

    def get_lines(self, satellite, scanline_dict):
        """Retrieve the best (highest elevation) lines of *scanline_dict*.
        """

        for utctime, hosts in scanline_dict.iteritems():
            hostname, elevation = max(hosts, key=(lambda x: x[1]))
            host = hostname.split(":")[0]

            logger.debug("requesting " +  " ".join([str(satellite),
                                                    str(utctime),
                                                    str(host)]))
            data = self._requesters[host].get_line(satellite, utctime)

            yield utctime, data, elevation



    def get_all(self, satellites):
        """Retrieve all the available scanlines from the stream, and save them.
        """
        sat_last_seen = {}
        sat_lines = {}
        for sat in satellites:
            sat_lines[sat] = {}
        queue = Queue()
        self.add_queue(queue)
        while True:
            try:
                sat, utctime, senders = queue.get(True,
                                                  CLIENT_TIMEOUT.seconds)
                if sat not in satellites:
                    continue
                sat_last_seen[sat] = datetime.utcnow()
                logger.debug("Picking line " + " ".join([str(utctime),
                                                     str(senders)]))
                # choose the highest elevation
                sender, elevation = max(senders, key=(lambda x: x[1]))
                logger.debug("requesting " +
                             " ".join([str(sat), str(utctime),
                                       str(sender), str(elevation)]))
                host = sender.split(":")[0]
                # TODO: this should be parallelized, and timed. I case of
                # failure, another source should be used. Choking ?
                line = self._requesters[host].get_line(sat, utctime)
                sat_lines[sat][utctime] = line
            except Empty:
                pass
            for sat, utctime in sat_last_seen.items():
                if utctime + CLIENT_TIMEOUT < datetime.utcnow():
                    # write the lines to file
                    logger.info(sat + " seems to be inactive now, writing file.")
                    first_time = min(sat_lines[sat].keys())
                    filename = first_time.isoformat() + sat + ".hmf"
                    with open(filename, "wb") as fp_:
                        for linetime in sorted(sat_lines[sat].keys()):
                            fp_.write(sat_lines[sat][linetime])
                    
                    del sat_last_seen[sat]
            
            

        

    def order(self, time_slice, satellite, filename):
        """Get all the scanlines for a *satellite* within a *time_slice* and
        save them in *filename*. The scanlines will be saved in a contiguous
        manner.
        """
        start_time = time_slice.start
        end_time = time_slice.stop

        saved = []


        # Create a file of the right length, filled with zeros. The alternative
        # would be to store all the scanlines in memory.
        tsize = (end_time - start_time).seconds * LINES_PER_SECOND * LINE_SIZE
        with open(filename, "wb") as fp_:
            fp_.write("\x00" * (tsize))
            
        # Do the retrieval.
        with open(filename, "r+b") as fp_:

            queue = Queue()
            self.add_queue(queue)

            linepos = None

            lines_to_get = {}

            # first, get the existing scanlines from self (client)
            logger.info("Getting list of existing scanlines from client.")
            for utctime, hosts in self.scanlines.get(satellite, {}).iteritems():
                if(utctime >= start_time and
                   utctime < end_time and
                   utctime not in saved):
                    lines_to_get[utctime] = hosts
                    
            # then, get scanlines from the server
            logger.info("Getting list of existing scanlines from server.")
            for host, req in self._requesters.iteritems():
                try:
                    response = req.get_slice(satellite, start_time, end_time)
                    for utcstr, elevation in response:
                        utctime = strp_isoformat(utcstr)
                        lines_to_get.setdefault(utctime, []).append((host,
                                                                     elevation))
                except IOError, e:
                    logger.warning(e)


                    
            # get lines with highest elevation and add them to current scene
            logger.info("Getting old scanlines.")
            for utctime, data, elevation in self.get_lines(satellite,
                                                           lines_to_get):
                if linepos is None:
                    linepos = compute_line_times(utctime, start_time, end_time)
                
                time_diff = utctime - start_time
                time_diff = (time_diff.seconds
                             + time_diff.microseconds / 1000000.0)
                pos = LINE_SIZE * int(np.floor(time_diff * LINES_PER_SECOND))
                fp_.seek(pos, 0)
                fp_.write(data)
                self.send_lineinfo_to_server(satellite, utctime, elevation,
                                             filename, pos)
                saved.append(utctime)
                linepos -= set([utctime])
            
            # then, get the newly arrived scanlines
            logger.info("Getting new scanlines")
            #timethres = datetime.utcnow() + CLIENT_TIMEOUT
            delay = timedelta(days=1000)
            timethres = datetime.utcnow() + delay
            while ((start_time > datetime.utcnow()
                    or timethres > datetime.utcnow())
                   and ((linepos is None) or (len(linepos) > 0))):
                try:
                    sat, utctime, senders = queue.get(True,
                                                      CLIENT_TIMEOUT.seconds)
                    logger.debug("Picking line " + " ".join([str(utctime),
                                                             str(senders)]))
                    # choose the highest elevation
                    sender, elevation = max(senders, key=(lambda x: x[1]))

                except Empty:
                    continue

                if linepos is None:
                    linepos = compute_line_times(utctime, start_time, end_time)

                if(sat == satellite and
                   utctime >= start_time and
                   utctime < end_time and
                   utctime not in saved):
                    saved.append(utctime)

                    # getting line
                    logger.debug("requesting " +
                                 " ".join([str(satellite), str(utctime),
                                           str(sender), str(elevation)]))
                    host = sender.split(":")[0]
                    # TODO: this should be parallelized, and timed. I case of
                    # failure, another source should be used. Choking ?
                    line = self._requesters[host].get_line(satellite, utctime)

                    # compute line position in file
                    time_diff = utctime - start_time
                    time_diff = (time_diff.seconds
                                 + time_diff.microseconds / 1000000.0)
                    pos = LINE_SIZE * int(np.floor(time_diff *
                                                   LINES_PER_SECOND))
                    fp_.seek(pos, 0)
                    fp_.write(line)
                    self.send_lineinfo_to_server(satellite, utctime, elevation,
                                                 filename, pos)
                    # removing from line check list
                    linepos -= set([utctime])

                    delay = min(delay, datetime.utcnow() - utctime)
                    if len(linepos) > 0:
                        timethres = max(linepos) + CLIENT_TIMEOUT + delay
                    else:
                        timethres = datetime.utcnow()

            # shut down
            self.del_queue(queue)
            print "Thanks for using pytroll/trollcast. See you soon on www.pytroll.org!"
            
    def send_lineinfo_to_server(self, *args, **kwargs):
        """Send information to our own server.
        """
        cfg = ConfigParser()
        cfg.read(self.cfgfile)
        host = cfg.get("local_reception", "localhost")
        host, port = (cfg.get(host, "hostname"),  cfg.get(host, "reqport"))
        del port
        self._requesters[host].send_lineinfo(*args, **kwargs)

    
    def stop(self):
        HaveBuffer.stop(self)
        for req in self._requesters.values():
            req.stop()

