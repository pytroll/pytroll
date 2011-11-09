#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011.

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

from posttroll.message import Message
from posttroll.bbmcast import MulticastReceiver, SocketTimeout

__all__ = ('AddressReceiver', 'getaddress')

debug = os.environ.get('DEBUG', False)
broadcast_port = 21200

#-----------------------------------------------------------------------------
#
# General thread to receive broadcast addresses.
#
#-----------------------------------------------------------------------------
class AddressReceiver(object):
    def __init__(self, name, max_age=timedelta(hours=1)):
        self._max_age = max_age
        self._address_lock = thread.allocate_lock()
        self._addresses = {}
        self._subject = '/%s/address' % name
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

    def get(self):
        now = datetime.now()
        addrs = []
        self._address_lock.acquire()
        try:
            for addr, atime in self._addresses.items():
                if now - atime < self._max_age:
                    addrs.append(addr)
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
        try:
            while self._do_run:
                try:
                    data, fromaddr = recv()
                    del fromaddr
                except SocketTimeout:
                    continue
                msg = Message.decode(data)
                if msg.type == 'info' and msg.subject.lower() == self._subject:
                    addr = [i.strip() for i in msg.data.split(':')]
                    addr[1] = int(addr[1])
                    addr = tuple(addr)
                    if debug:
                        print 'receiving address', addr
                    self._add(addr)
        finally:
            self._is_running = False
            recv.close()

    def _add(self, adr):
        self._address_lock.acquire()
        try:
            self._addresses[adr] = datetime.now()
        finally:
            self._address_lock.release()

#-----------------------------------------------------------------------------
# default
getaddress = AddressReceiver


