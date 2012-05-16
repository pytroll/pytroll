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

"""Different kinds of connections to the datacenter. These classes collect
datacenter addresses for further use.
"""

import zmq

from posttroll.address_receiver import getaddress

class GenericConnections(object):
    """Datacenter connections manager.
    """
    def __init__(self, module_name):
        self._dc_addresses = getaddress(module_name)
        self._context = zmq.Context()
        self._connections = {}

    def get_addresses(self):
        """Return the addresses
        """
        return self._dc_addresses.get()        

    def get_address_by_type(self, atype):
        """Return the address(es) corresponding to *atype*.
        """
        return [addr for addr in self.get_addresses() if addr["type"] == atype]


    def start(self):
        """Start datacenter address gathering.
        """
        self._dc_addresses.start()
        return self
    
    def stop(self):
        """Stop datacenter address gathering.
        """
        self._dc_addresses.stop()
        for sock in self._connections.values():
            sock.close()
        self._connections = {}
