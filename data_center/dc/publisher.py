#
# Copyright (c) 2009.
#
# DMI
# Lyngbyvej 100
# DK-2100 Copenhagen
# Denmark
#
# Author(s): 
#   Lars Orum Rasmussen
#   Martin Raspaud

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import zmq
from threading import Thread

class Publisher(object):
    """The publisher class.
    """
    def __init__(self, address):
        """Bind the publisher class to a port.
        """
        self.destination = address
        self.context = zmq.Context()
        self.publish = self.context.socket(zmq.PUB)
        self.publish.bind(self.destination)
    
    def send(self, msg):
        """Send the given message.
        """
        self.publish.send(msg)
