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
from datetime import datetime
from urlparse import urlsplit, urlunsplit, SplitResult
from posttroll.publisher import Publish
from posttroll.subscriber import Subscriber
from posttroll.message import Message
import logging

logger = logging.getLogger(__name__)

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
    #return utctime.strftime("%Y%m%dT%H%M%S") + "_".join(satellite.split(" "))
    return utctime, "_".join(satellite.split(" "))

class PassRecorder(dict):
    def get(self, key, default=None):
        utctime, satellite = key
        for (rectime, recsat), val in self.iteritems():
            if(recsat == satellite and
               (abs(rectime - utctime)).seconds < 5 and
               (abs(rectime - utctime)).days == 0):
                return val
        return default
            
            


class MessageReceiver(object):
    """Interprets received messages between stop reception and file dispatch.
    """

    def __init__(self):
        self._received_passes = PassRecorder()
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
        del pass_info['risetime']
        pass_info["end_time"] = datetime.strptime(pass_info["falltime"],
                                                  "%Y-%m-%d %H:%M:%S")
        del pass_info['falltime']

        if 'orbit number' in pass_info:
            pass_info['orbit_number'] = int(pass_info['orbit number'])
            del pass_info['orbit number']
        else:
            LOG.warning("No 'orbit number' in message!")

        
        pname = pass_name(pass_info["start_time"], pass_info["satellite"])
        self._received_passes[pname] = pass_info

    def clean_passes(self, days=1):
        oldies = []

        for key, val in self._received_passes.iteritems():
            if (datetime.utcnow() - val["start_time"]).days >= days:
                oldies.append(key)

        for key in oldies:
            del self._received_passes[key]

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
            instruments = {"0064": "modis",
                           "0141": "ceres+y",
                           "0157": "ceres-y",
                           "0261": "amsu-a1",
                           "0262": "amsu-a1",
                           "0290": "amsu-a2",
                           "0342": "hsb",
                           "0402": "amsr-e",
                           "0404": "airs",
                           "0405": "airs",
                           "0406": "airs",
                           "0407": "airs",
                           "0414": "airs",
                           "0415": "airs",
                           "0419": "airs",
                           "0957": "gbad",
                           }
            swath["instrument"] = instruments.get(pds["apid1"][3:],
                                                  pds["apid1"][3:])
            swath["format"] = "PDS"
            swath["type"] = "EOS 0"
            swath["number"] = int(pds["ufn"])

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
            swath["format"] = "HDF5"
            swath["type"] = "RDR"

        else:
            return

        if pathname2.endswith(filename):
            uri = pathname2
        else:
            uri = os.path.join(pathname2, filename)

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
            
def receive_from_zmq(days=1):
    """Receive 2met! messages from zeromq.
    """
    
    socket = Subscriber(["tcp://localhost:9331"], ["2met!"])
    
    mr = MessageReceiver()
    logger.debug("setting up publishers")
    print "setting up publishers"
    import sys
    sys.stdout.flush()

    with Publish("receiver", "HRPT 0", 9000) as hrpt_pub:
        with Publish("receiver", "EOS 0", 9001) as pds_pub:
            with Publish("receiver", "RDR", 9002) as npp_pub:
                for rawmsg in socket.recv():
                    # TODO:
                    # - Watch for idle time in order to detect a hangout
                    # - make recv interruptible.
                    logger.debug("receive from 2met! " + str(rawmsg))
                    string = TwoMetMessage(rawmsg.data)
                    to_send = mr.receive(string)
                    if to_send is None:
                        continue
                    msg = Message('/oper/polar/direct_readout/norrköping', "file",
                                  to_send).encode()
                    logger.debug("publishing " + str(msg))
                    if to_send["type"] == "HRPT 0":
                        hrpt_pub.send(msg)
                    if to_send["type"] == "EOS 0":
                        pds_pub.send(msg)
                    if to_send["type"] == "RDR":
                        npp_pub.send(msg)
                    if days:
                        mr.clean_passes(days)

if __name__ == '__main__':
    logging.basicConfig(filename='mylog_npp.log',level=logging.DEBUG)
    logger = logging.getLogger("Receiver")
    try:
        receive_from_zmq(1)
    except KeyboardInterrupt:
        print ("Thank you for using pytroll/receiver."
               " See you soon on pytroll.org!")



