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

"""Receiver for 2met messages, through zeromq.
"""
import os
import zmq
from datetime import datetime
from urlparse import urlsplit, urlunsplit, urlparse, SplitResult
from socket import gethostname
from posttroll.publisher import Publish
from posttroll.message import Message
import logging

logging.basicConfig(filename='mylog_npp.log',level=logging.DEBUG)

EMITTER = "nimbus.smhi.se"

class TwoMetMessage(object):
    """Interperter for 2met! messages.
    """
    
    def __init__(self, mstring=None):
        self._id = 0
        self._type = ""
        self._time = datetime.utcnow()
        self.body = ''
        if mstring is not None:
            self._decode(mstring.strip())

    def _decode(self, mstring):
        """Decode 2met! messages.
        """
        dummy, content = mstring.split("[", 1)
        content = content.rsplit("]", 1)[0]
        dic = dict((item.split("=", 1) for item in content.split(", ", 3)))
        self._id = eval(dic["ID"])
        self._time = datetime.strptime(eval(dic["time"]), "%d %m %Y - %H:%M:%S")
        try:
            self.body = eval(dic["body"])
        except SyntaxError:
            self.body = str(dic["body"])
        self._type = eval(dic["type"])

def pass_name(utctime, satellite):
    """Construct a unique pass name from a risetime and a satellite name.
    """
    return utctime.strftime("%Y%m%dT%H%M%S") + "_".join(satellite.split(" "))



class MessageReceiver(object):
    """Interprets received messages between stop reception and file dispatch.
    """

    def __init__(self):
        self._received_passes = {}
        self._distributed_files = {}

    def add_pass(self, message):
        """Formats pass info and adds it to the object.
        """
        info = dict((item.split(": ", 1) for item in message.split(", ", 3)))
        pass_info = {}
        for key, val in info.items():
            pass_info[key.lower()] = val
        pass_info["start_time"] = datetime.strptime(pass_info["risetime"],
                                                  "%Y-%m-%d %H:%M:%S")
        pass_info["end_time"] = datetime.strptime(pass_info["falltime"],
                                                  "%Y-%m-%d %H:%M:%S")

        pname = pass_name(pass_info["start_time"], pass_info["satellite"])
        self._received_passes[pname] = pass_info

    def handle_distrib(self, message):
        """React to a file dispatch message.
        """

        pathname1, pathname2 = message.split(" ")
        dummy, filename = os.path.split(pathname1)
        # TODO: Should not make any assumptions on filename formats, should
        # load a description of it from a config file instead.
        if pathname1.endswith(".hmf"):
            risestr, satellite = filename[:-4].split("_", 1)
            risetime = datetime.strptime(risestr, "%Y%m%d%H%M%S")
            pname = pass_name(risetime, satellite)
            swath = self._received_passes.get(pname, {"satellite": satellite,
                                                      "start_time": risetime})
            swath["type"] = "HRPT 0"
            if satellite == "FENGYUN_1D":
                swath["format"] = "CHRPT"
            else:
                swath["format"] = "16-bit HRPT Minor Frame"
            if pathname2.endswith(".hmf"):
                uri = pathname2
            else:
                uri = os.path.join(pathname2, filename)

        elif filename.startswith("P042") or filename.startswith("P154"):
            pds = {}
            pds["format"] = filename[0]
            pds["apid1"] = filename[1:8]
            pds["apid2"] = filename[8:15]
            pds["apid3"] = filename[15:22]
            pds["time"] = datetime.strptime(filename[22:33], "%y%j%H%M%S")
            pds["nid"] = filename[33]
            pds["ufn"] = filename[34:36]
            pds["extension"] = filename[36:40]
            if pds["apid1"][:3] == "042":
                satellite = "TERRA"
            elif pds["apid1"][:3] == "154":
                satellite = "AQUA"
            else:
                raise ValueError("Unrecognized satellite ID: " + pds["apid1"][:3])
            risetime = pds["time"]
            pname = pass_name(risetime, satellite)
            swath = self._received_passes.get(pname, {"satellite": satellite,
                                                      "start_time": risetime})
            instruments = {"0064": "modis"}
            swath["instrument"] = instruments.get(pds["apid1"][3:],
                                                  pds["apid1"][3:])
            swath["format"] = "PDS"
            swath["type"] = "EOS 0"
            swath["number"] = int(pds["ufn"])
            uri = os.path.join(pathname2, filename)

        elif filename.startswith("R") and filename.endswith(".h5"):
            mda = {}
            mda["format"] = filename[0]
            if filename.startswith("RATMS-RNSCA"):
                mda["instrument"] = "atms"
            elif filename.startswith("RCRIS-RNSCA"):
                mda["instrument"] = "cris"
            elif filename.startswith("RNSCA-RVIRS"):
                mda["instrument"] = "viirs"
            mda["time"] = datetime.strptime(filename[16:33], "d%Y%m%d_t%H%M%S")
            mda["orbit"] = filename[45:50]
            satellite = "NPP"
            risetime = mda["time"]
            pname = pass_name(risetime, satellite)
            swath = self._received_passes.get(pname, {"satellite": satellite,
                                                      "start_time": risetime})
            swath["instrument"] = mda["instrument"]
            swath["format"] = "HDF"
            swath["type"] = "RDR"
            uri = os.path.join(pathname2, filename)

        else:
            return

        url = urlsplit(uri)
        if url.scheme in ["", "file"]:
            scheme = "ssh"
            netloc = EMITTER
            uri = urlunsplit(SplitResult(scheme,
                                         netloc,
                                         url.path,
                                         url.query,
                                         url.fragment))
        elif url.scheme == "ftp":
            scheme = "ssh"
            netloc = url.hostname
            uri = urlunsplit(SplitResult(scheme,
                                         netloc,
                                         url.path,
                                         url.query,
                                         url.fragment))
        swath["filename"] = os.path.split(url.path)[1] 
        swath["uri"] = uri
        return swath

        # TODO: remove pass when all file dispatches have been send, or after a timeout ?
        
    def receive(self, message):
        """Receive the messages and triage them.
        """
        metadata_prefix = "STOPRC Stop reception: "
        dispatch_prefix = "FILDIS File Dispatch: "
        if message.body.startswith(metadata_prefix):
            self.add_pass(message.body[len(metadata_prefix):])
            return None
        
        elif message.body.startswith(dispatch_prefix):
            return self.handle_distrib(message.body[len(dispatch_prefix):])
            
def receive_from_zmq():
    """Receive 2met! messages from zeromq.
    """
    
    # Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:9332")

    #filter = "Message"
    socket.setsockopt(zmq.SUBSCRIBE, "")
    mr = MessageReceiver()
    logging.debug("setting up publishers")
    print "setting up publishers"
    import sys
    sys.stdout.flush()

    with Publish("receiver", "HRPT 0", 9000) as hrpt_pub:
        with Publish("receiver", "EOS 0", 9001) as pds_pub:
            with Publish("receiver", "RDR", 9002) as npp_pub:
                while True:
                    logging.debug("waiting for messages")
                    # TODO:
                    # - Watch for idle time in order to detect a hangout
                    # - make recv interruptible.
                    rawmsg = socket.recv()
                    logging.debug("receive from 2met! " + str(rawmsg))
                    string = TwoMetMessage(rawmsg)
                    to_send = mr.receive(string)
                    if to_send is None:
                        continue
                    try:
                        logging.debug(to_send)
                        to_send["start_time"] = to_send["start_time"].isoformat()
                        to_send["end_time"] = to_send["end_time"].isoformat()
                    except AttributeError:
                        pass
                    except KeyError:
                        pass
                    msg = Message('/oper/polar/direct_readout/norrkÃping', "file",
                                  to_send).encode()
                    logging.debug("publishing " + str(msg))
                    if to_send["type"] == "HRPT 0":
                        hrpt_pub.send(msg)
                    if to_send["type"] == "EOS 0":
                        pds_pub.send(msg)
                    if to_send["type"] == "RDR":
                        npp_pub.send(msg)

TEST_DATA_NPP = """Message[ID='0', type='2met.message', time='15 03 2012 - 12:18:06', body='STOPRC Stop reception: Satellite: NPP, Orbit number: 1974, Risetime: 2012-03-15 12:02:48, Falltime: 2012-03-15 12:18:06']
"""


TEST_DATA_NOAA19 = """Message[ID='0', type='2met.message', time='12 01 2012 - 11:35:20', body='STOPRC Stop reception: Satellite: NOAA 19, Orbit number: 15090, Risetime: 2012-01-12 11:19:32, Falltime: 2012-01-12 11:35:20']
Message[ID='0', type='2met.message', time='12 01 2012 - 11:35:20', body='STOPRC HRPTFrameSync stops reception. Rename raw data file to /data/hrpt/20120112111932_NOAA_19.hmf']
Message[ID='0', type='2met.message', time='12 01 2012 - 11:35:20', body='STOPRC HRPTFrameSync closed analyze file']
Message[ID='8250', type='2met.filehandler.sink.success', time='12 01 2012 - 11:35:23', body='FILDIS File Dispatch: /data/hrpt/20120112111932_NOAA_19.hmf /archive/hrpt/20120112111932_NOAA_19.hmf']
Message[ID='8250', type='2met.filehandler.sink.success', time='12 01 2012 - 11:35:25', body='FILDIS File Dispatch: /data/hrpt/20120112111932_NOAA_19.hmf ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/hrpt']
Message[ID='8250', type='2met.filehandler.sink.success', time='12 01 2012 - 11:35:26', body='FILDIS File Dispatch: /data/hrpt/20120112111932_NOAA_19.hmf ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/hrpt']"""

TEST_DATA_TERRA = """Message[ID='0', type='2met.message', time='23 01 2012 - 22:10:25', body='STOPRC Stop reception: Satellite: TERRA, Orbit number: 64360, Risetime: 2012-01-23 21:57:43, Falltime: 2012-01-23 22:10:25']
Message[ID='0', type='2met.message', time='23 01 2012 - 22:10:25', body='STOPRC Send HW Controller the stopReception command']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:00', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743001.PDS /archive/modis/P0420064AAAAAAAAAAAAAA12023215743001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:00', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743000.PDS /archive/modis/P0420064AAAAAAAAAAAAAA12023215743000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:02', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:03', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:03', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:03', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:04', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:04', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']"""
TEST_DATA_AQUA = """Message[ID='0', type='2met.message', time='24 01 2012 - 00:35:21', body='STOPRC Stop reception: Satellite: AQUA, Orbit number: 51722, Risetime: 2012-01-24 00:21:39, Falltime: 2012-01-24 00:35:21']
Message[ID='0', type='2met.message', time='24 01 2012 - 00:35:21', body='STOPRC Send HW Controller the stopReception command']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540342AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540064AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540220AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540290AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540141AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540114AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540290AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540261AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540157AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540404AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540407AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540414AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540415AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540414AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540404AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540266AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540406AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540220AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540064AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540262AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540405AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540407AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540266AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540405AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540141AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540262AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540406AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139001.PDS /archive/modis/P15409571540958154095912024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540261AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540342AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540114AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139000.PDS /archive/modis/P15409571540958154095912024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540415AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540157AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:16', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:17', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:17', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:17', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:17', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:18', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:18', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:18', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:18', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:20', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:20', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:20', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:22', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:22', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:22', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:22', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:23', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:23', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:26', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:26', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:26', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:26', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:26', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:29', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:29', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:29', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:29', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:29', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:30', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:30', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:30', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:30', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:31', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:31', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:32', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:32', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:32', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:32', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:33', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:33', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:34', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:34', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:34', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:34', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:35', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:35', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:35', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:36', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:36', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:36', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:37', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:37', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:37', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:38', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:38', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:38', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:38', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:39', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:39', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:39', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']"""

def test_read(test_data):
    lines = test_data.split("\n")
    mr = MessageReceiver()
    for line in lines:
        to_send = mr.receive(TwoMetMessage(line))
        if to_send:
            try:
                to_send["risetime"] = to_send["risetime"].isoformat()
                to_send["falltime"] = to_send["falltime"].isoformat()
            except AttributeError:
                pass
            msg = Message('/oper/polar/direct_readout/norrköping', "file",
                          to_send).encode()
            print "Should publish", msg

if __name__ == '__main__':
    receive_from_zmq()
    #test_read(TEST_DATA_NOAA19)
    #test_read(TEST_DATA_TERRA)
    #test_read(TEST_DATA_AQUA)




# cleaning
# To be filtered out: Message[ID='20300', type='egmc2.action.submitted', time='27 01 2012 - 12:44:19', body='Command 2met.control.limit::clean[[]] has been submitted, current feedback is ${feedback}.']
# New Message: Message[ID='20300', type='egmc2.action.submitted', time='27 01 2012 - 12:44:19', body='Command 2met.control.limit::clean[[]] has been submitted, current feedback is ${feedback}.']
# To be filtered out: Message[ID='8100', type='2met.limit.success', time='27 01 2012 - 12:44:19', body='LIMSUC File LIMIT was called with target clean. Limit Files by Age: checked 4 target directories and deleted 4 files. Limit Files by Counts: checked 2 target directories and deleted 0 files.']
# New Message: Message[ID='8100', type='2met.limit.success', time='27 01 2012 - 12:44:19', body='LIMSUC File LIMIT was called with target clean. Limit Files by Age: checked 4 target directories and deleted 4 files. Limit Files by Counts: checked 2 target directories and deleted 0 files.']
# To be filtered out: Message[ID='20302', type='egmc2.action.finished', time='27 01 2012 - 12:44:19', body='Command 2met.control.limit::clean[[]] has been finished, feedback is FIN [958942024] - code=0, value=Limit Files by Age: checked 4 target directories and deleted 4 files. Limit Files by Counts: checked 2 target directories and deleted 0 files..']
# New Message: Message[ID='20302', type='egmc2.action.finished', time='27 01 2012 - 12:44:19', body='Command 2met.control.limit::clean[[]] has been finished, feedback is FIN [958942024] - code=0, value=Limit Files by Age: checked 4 target directories and deleted 4 files. Limit Files by Counts: checked 2 target directories and deleted 0 files..']
