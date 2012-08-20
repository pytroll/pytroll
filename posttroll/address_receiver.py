#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012.

# Author(s):
 
#   Lars Ø. Rasmussen <ras@dmi.dk>
#   Martin Raspaud <martin.raspaud@smhi.se>

# This file is part of pytroll.

# Pytroll is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.

# Pytroll is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# pytroll.  If not, see <http://www.gnu.org/licenses/>. 

"""
Receive broadcasted addresses in a standard pytroll Message:
/<server-name>/address info ... host:port
"""

import os
from datetime import datetime, timedelta
import thread
import threading
import copy

from posttroll.message import Message
from posttroll.bbmcast import MulticastReceiver, SocketTimeout
from posttroll.publisher import Publish

__all__ = ('AddressReceiver', 'getaddress')

debug = os.environ.get('DEBUG', False)
broadcast_port = 21200

default_publish_port = 16543

#-----------------------------------------------------------------------------
#
# General thread to receive broadcast addresses.
#
#-----------------------------------------------------------------------------
class AddressReceiver(object):
    def __init__(self, name="", max_age=timedelta(hours=1), port=None):
        self._max_age = max_age
        self._port = port or default_publish_port 
        self._address_lock = thread.allocate_lock()
        self._addresses = {}
        self._subject = '/address'
        self._name = name
        self._do_run = False
        self._is_running = False
        self._thread = threading.Thread(target=self._run)        

    def start(self):
        if not self._is_running:
            self._do_run = True
            self._thread.start()
        return self

    def stop(self):
        self._do_run = False
        return self

    def is_running(self):
        return self._is_running

    def get(self, name=""):
        now = datetime.utcnow()
        addrs = []
        name = name or self._name
        self._address_lock.acquire()
        try:
            for addr, metadata in self._addresses.items():
                atime = metadata["receive_time"]
                if now - atime < self._max_age:
                    mda = copy.copy(metadata)
                    mda["receive_time"] = mda["receive_time"].isoformat()
                    addrs.append(mda)
                else:
                    del self._addresses[addr]
        finally:
            self._address_lock.release()
        if debug:
            print 'return address', addrs
        return addrs

    def _run(self):
        port = broadcast_port
        recv = MulticastReceiver(port).settimeout(2.0)
        self._is_running = True
        with Publish("address_receiver", ["addresses"], self._port) as pub:
            try:
                while self._do_run:
                    try:
                        data, fromaddr = recv()
                        del fromaddr
                    except SocketTimeout:
                        continue
                    msg = Message.decode(data)
                    name = msg.subject.split("/")[1]
                    if(msg.type == 'info' and
                       msg.subject.lower().endswith(self._subject)):
                        addr = msg.data["URI"]
                        metadata = copy.copy(msg.data)
                        metadata["name"] = name
                        if debug:
                            print 'receiving address', addr, name, metadata
                        if addr not in self._addresses:
                            pub.send(str(msg))
                            if debug:
                                print 'publishing address', addr, name, metadata
                        self._add(addr, metadata)
            finally:
                self._is_running = False
                recv.close()

    def _add(self, adr, metadata):
        self._address_lock.acquire()
        try:
            metadata["receive_time"] = datetime.utcnow()
            self._addresses[adr] = metadata
        finally:
            self._address_lock.release()

#-----------------------------------------------------------------------------
# default
getaddress = AddressReceiver


