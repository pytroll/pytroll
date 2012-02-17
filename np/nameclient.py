#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011 SMHI

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

"""Asking for the address of a module.
"""

import zmq

class TimeoutException(BaseException):
    pass

def get_address(data_type, timeout=2):

    context = zmq.Context()

    # Socket to talk to server
    socket = context.socket(zmq.REQ)
    try:
        socket.connect("tcp://localhost:5555")

        socket.send (data_type)

        # Get the reply.
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)
        s = poller.poll(timeout=timeout * 1000)
        if s:
            if s[0][0] == socket:
                m = socket.recv(zmq.NOBLOCK)
                return m
            else:
                raise RuntimeError("Unknown socket ?!?!?")
        else:
            raise TimeoutException("Didn't get an address after %d seconds."
                                   %timeout)
        print "Received reply to ", data_type, ": [", m, "]"
    finally:
        socket.close()
