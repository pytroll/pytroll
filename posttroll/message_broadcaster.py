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

import os
import time
import threading

import posttroll.message as message
from posttroll.bbmcast import MulticastSender, MC_GROUP

__all__ = ('MessageBroadcaster', 'AddressBroadcaster', 'sendaddress')

debug = os.environ.get('DEBUG', False)
broadcast_port = 21200

#-----------------------------------------------------------------------------
#
# General thread to broadcast messages.
#
#-----------------------------------------------------------------------------
class MessageBroadcaster(object):
    """Class to broadcast stuff.
    """
    def __init__(self, msg, port, interval):
        # mcgroup = None or '<broadcast>' is broadcast
        # mcgroup = MC_GROUP is default multicast group
        self._sender = MulticastSender(port, mcgroup=MC_GROUP)
        self._interval = interval
        self._message = msg
        self._do_run = False
        self._is_running = False
        self._thread = threading.Thread(target=self._run)
        
    def start(self):
        """Start the broadcasting.
        """
        if not self._is_running:
            self._do_run = True
            self._thread.start()
        return self

    def is_running(self):
        """Are we running.
        """
        return self._is_running

    def stop(self):
        """Stop the broadcasting.
        """
        self._do_run = False
        return self

    def _run(self):
        """Broadcasts forever.
        """
        self._is_running = True
        try:
            while self._do_run:
                if debug:
                    print "Advertizing.", str(self._message)
                self._sender(self._message)
                time.sleep(self._interval)
        finally:
            self._is_running = False
            self._sender.close()

#-----------------------------------------------------------------------------
#
# General thread to broadcast addresses.
#
#-----------------------------------------------------------------------------
class AddressBroadcaster(MessageBroadcaster):
    """Class to broadcast stuff.
    """
    def __init__(self, name, address, interval):
        msg = message.Message("/%s/address"%name, "info",
                              "%s:%d"%address).encode()
        MessageBroadcaster.__init__(self, msg, broadcast_port, interval) 
#-----------------------------------------------------------------------------
# default
sendaddress = AddressBroadcaster
