#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, 2013, 2014 SMHI

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

Outputs messages with the following metadata:
satellite, format, start_time, end_time, filename, uri, type, orbit_number, [instrument, number]

"""
import os
from datetime import datetime
from time import sleep
from urlparse import urlsplit, urlunsplit, SplitResult
from posttroll.publisher import Publish
from posttroll.message import Message
from lxml import etree
import logging
import socket

logger = logging.getLogger(__name__)

LOOP = True

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
        self._attrs = {}

    def _internal_decode(self, mstring):
        """Decode 2met! messages, internal format.
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

    def _xml_decode(self, mstring):
        """Decode xml 2met! messages.
        """
        root = etree.fromstring(mstring)
        self._attrs = dict(root.items())

        self._id = int(root.get("sequence"))
        self._type = root.get("type")
        self._time = datetime.strptime(root.get("timestamp"),
                                       "%Y-%m-%dT%H:%M:%S")
        for child in root:
            if child.tag == "body":
                self.body = child.text



    def _decode(self, mstring):
        """Decode 2met! messages.
        """

        if mstring.startswith("Message["):
            self._internal_decode(mstring)
        elif mstring.startswith("<message"):
            try:
                self._xml_decode(mstring)
            except:
                logger.exception("Spurious message! " + str(mstring))
        else:
            logger.warning("Don't know how to decode message: " + str(mstring))
        
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
               (abs(rectime - utctime)).seconds < 30 * 60 and
               (abs(rectime - utctime)).days == 0):
                return val
        return default
            
            
class MessageReceiver(object):
    """Interprets received messages between stop reception and file dispatch.
    """

    def __init__(self, emitter):
        self._received_passes = PassRecorder()
        self._distributed_files = {}
        self._emitter = emitter

    def add_pass(self, message):
        """Formats pass info and adds it to the object.
        """
        info = dict((item.split(": ", 1) for item in message.split(", ", 3)))
        logger.info("Adding pass: " + str(info))
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
            logger.warning("No 'orbit number' in message!")

        
        pname = pass_name(pass_info["start_time"], pass_info["satellite"])
        self._received_passes[pname] = pass_info

    def clean_passes(self, days=1):
        """Clean old passes from the pass dict (_received_passes).
        """
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
            swath["type"] = "binary"
            if satellite == "FENGYUN_1D":
                swath["format"] = "CHRPT"
            else:
                swath["format"] = "HRPT"
                swath["instrument"] = ("avhrr/3", "mhs", "amsu")
            swath["level"] = "0"
            

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
            swath["type"] = "binary"
            swath["level"] = "0"
            swath["number"] = int(pds["ufn"])

        # NPP RDRs
        elif filename.startswith("R") and filename.endswith(".h5"):
            # Occassionaly RT-STPS produce files with a nonstandard file
            # naming, lacking the 'RNSCA' field. We will try to deal with this
            # below (Adam - 2013-06-04):
            mda = {}
            idx_start = 0
            mda["format"] = filename[0]
            if filename.startswith("RATMS-RNSCA"):
                mda["instrument"] = "atms"
            elif filename.startswith("RCRIS-RNSCA"):
                mda["instrument"] = "cris"
            elif filename.startswith("RNSCA-RVIRS"):
                mda["instrument"] = "viirs"
            else:
                if filename.startswith("RATMS_npp"):
                    mda["instrument"] = "atms"
                elif filename.startswith("RCRIS_npp"):
                    mda["instrument"] = "cris"
                else:
                    logger.warning("Seems to be a NPP/JPSS RDR " + 
                                   "file but name is not standard!")
                    logger.warning("filename = " + filename)
                    return None
                idx_start = -6

            mda["start_time"] = datetime.strptime(filename[idx_start+16:idx_start+33], 
                                                  "d%Y%m%d_t%H%M%S")
            end_time = datetime.strptime(filename[idx_start+16:idx_start+25] + 
                                         " " + 
                                         filename[idx_start+35:idx_start+42],
                                         "d%Y%m%d e%H%M%S")
            mda["orbit"] = filename[idx_start+45:idx_start+50]
            # FIXME: swath start and end time is granule dependent.
            # Get the end time as well! - Adam 2013-06-03:            
            satellite = "NPP"
            start_time = mda["start_time"]
            pname = pass_name(start_time, satellite)

            swath = self._received_passes.get(pname, {"satellite": satellite,
                                                      "start_time": start_time})
            swath['end_time'] = end_time
            swath["instrument"] = mda["instrument"]
            swath["format"] = "RDR"
            swath["type"] = "HDF5"
            swath["level"] = "0"

        # metop
        elif filename[4:12] == "_HRP_00_":
            instruments = {"AVHR": "avhrr",
                           "ASCA": "ascat",
                           "AMSA": "amsu-a",
                           "ASCA": "ascat",
                           "ATOV": "atovs",
                           "AVHR": "avhrr/3",
                           "GOME": "gome",
                           "GRAS": "gras",
                           "HIRS": "hirs/4",
                           "IASI": "iasi",
                           "MHSx": "mhs",
                           "SEMx": "sem",
                           "ADCS": "adcs",
                           "SBUV": "sbuv",
                           "HKTM": "vcdu34"}

            satellites = {"M02": "METOP-A",
                          "M01": "METOP-B"}

            satellite = satellites[filename[12:15]]
            risetime = datetime.strptime(filename[16:31], "%Y%m%d%H%M%SZ")
            #falltime = datetime.strptime(filename[16:47], "%Y%m%d%H%M%SZ")

            pname = pass_name(risetime, satellite)
            swath = self._received_passes.get(pname, {"satellite": satellite,
                                                      "start_time": risetime})
            swath["instrument"] = instruments[filename[:4]]
            swath["format"] = "EPS"
            swath["type"] = "binary"
            swath["level"] = "0"
        else:
            return None

        if pathname2.endswith(filename):
            uri = pathname2
        else:
            uri = os.path.join(pathname2, filename)

        url = urlsplit(uri)
        if url.scheme in ["", "file"]:
            scheme = "ssh"
            netloc = self._emitter
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

class GMCSubscriber(object):

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sock = None
        self.msg = ""
        self._bufsize = 256
        self.loop = True
        
    def recv(self):
        """Receive messages.
        """
        while LOOP:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self._sock.connect((self._host, self._port))
            except socket.error:
                logger.error("Cannot connect to " + str((self._host, self._port))
                             + ", retrying in 60 seconds.")
                sleep(60)
                continue
            self._sock.settimeout(1.0)
            try:
                while LOOP:
                    try:
                        data = self._sock.recv(self._bufsize)
                    except socket.timeout:
                        pass
                    else:
                        if not data:
                            break
                        self.msg += data
                        messages = self.msg.split("</message>")
                        if len(messages) > 1:
                            for mess in messages[:-1]:
                                yield mess + "</message>"
                            if messages[-1].endswith("</body>"):
                                yield messages[-1] + "</message>"
                                self.msg = ""
                            else:
                                self.msg = messages[-1]
                        elif self.msg.endswith("</message>"):
                            yield self.msg
                            self.msg = ""
            finally:
                self._sock.close()

def receive_from_zmq(host, port, station, environment, days=1):
    """Receive 2met! messages from zeromq.
    """

    #socket = Subscriber(["tcp://localhost:9331"], ["2met!"])
    sock = GMCSubscriber(host, port)
    msg_rec = MessageReceiver(host)

    with Publish("receiver", 0, ["HRPT 0", "PDS", "RDR", "EPS 0"]) as pub:
        for rawmsg in sock.recv():
            # TODO:
            # - Watch for idle time in order to detect a hangout
            logger.debug("receive from 2met! " + str(rawmsg))
            string = TwoMetMessage(rawmsg)
            to_send = msg_rec.receive(string)
            if to_send is None:
                continue
            subject = "/".join((to_send['format'], to_send['level'],
                                station, environment,
                                "polar", "direct_readout"))

            msg = Message(subject,
                          "file",
                          to_send).encode()
            logger.debug("publishing " + str(msg))
            pub.send(msg)
            if days:
                msg_rec.clean_passes(days)

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="GMC host")
    parser.add_argument("port", help="Port to listen to", type=int)
    parser.add_argument("-s", "--station", help="Name of the station",
                        default="unknown")
    parser.add_argument("-e", "--environment",
                        help="Name of the environment (e.g. dev, test, oper)",
                        default="dev")
    parser.add_argument("-d", "--daemon", help="Run as a daemon",
                        choices=["start", "stop", "status", "restart"])
    parser.add_argument("-l", "--log", help="File to log to", default=None)
    opts = parser.parse_args()
    
    if opts.log:
        import logging.handlers
        handler = logging.handlers.TimedRotatingFileHandler(opts.log,
                                                            "midnight",
                                                            backupCount = 7)
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(logging.Formatter("[%(levelname)s: %(asctime)s :"
                                                " %(name)s] %(message)s",
                                                '%Y-%m-%d %H:%M:%S'))
    handler.setLevel(logging.DEBUG)
    logging.getLogger('').setLevel(logging.DEBUG)
    logging.getLogger('').addHandler(handler)
    logger = logging.getLogger("receiver")

    if opts.daemon is None:
        try:
            receive_from_zmq(opts.host, opts.port,
                             opts.station, opts.environment, 1)
        except KeyboardInterrupt:
            pass
        except:
            logger.exception("Something wrong happened...")
        finally:
            print ("Thank you for using pytroll/receiver."
                   " See you soon on pytroll.org!")

    else: # Running as a daemon
        import sys
        #pidfile = '/tmp/pytroll.receiver.pid'
        pidfile = '/var/run/satellit/pytroll.receiver.pid'
        
        if opts.daemon == "status":
            if os.path.exists(pidfile):
                with open(pidfile) as fd_:
                    pid = int(fd_.read())
                    try:
                        os.kill(pid, 0)
                    except OSError:
                        sys.exit(1)
                    else:
                        sys.exit(0)
            else:
                sys.exit(1)

        def _terminate(*args):
            """terminate the receiver.
            """
            del args
            global LOOP
            LOOP = False

        def _main(*args):
            """Run the receiver.
            """
            del args
            try:
                receive_from_zmq(opts.host, opts.port, 1)
            except:
                logger.exception("Crashed.")
                raise

        try:
            import daemon.runner
            import signal

            class App(object):
                """App object for running the nameserver as daemon.
                """
                stdin_path = "/dev/null"
                stdout_path = "/dev/null"
                stderr_path = "/dev/null"
                run = _main
                pidfile_path = pidfile
                pidfile_timeout = 90

                
            signal.signal(signal.SIGTERM, _terminate)


            APP = App()
            sys.argv = [sys.argv[0], opts.daemon]
            angel = daemon.runner.DaemonRunner(APP)
            angel.daemon_context.files_preserve = [handler.stream]
            angel.parse_args([sys.argv[0], opts.daemon])
            sys.exit(angel.do_action())
        except ImportError:
            print "Cannot run as a daemon, you need python-daemon installed."


