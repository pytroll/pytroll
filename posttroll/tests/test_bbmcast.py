#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011.

# Author(s):
 
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

import unittest
import random
from socket import SOL_SOCKET, SO_BROADCAST, error

from posttroll import bbmcast


class Test(unittest.TestCase):
    """Test class.
    """

    def test_mcast_sender(self):
        """Unit test for mcast_sender.
        """
        mcgroup = (str(random.randint(224, 239)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)))
        socket, group = bbmcast.mcast_sender(mcgroup)
        if mcgroup in ("0.0.0.0", "255.255.255.255"):
            self.assertEquals(group, "<broadcast>")
            self.assertEquals(socket.getsockopt(SOL_SOCKET, SO_BROADCAST), 1)
        else:
            self.assertEquals(group, mcgroup)
            self.assertEquals(socket.getsockopt(SOL_SOCKET, SO_BROADCAST), 0)

        socket.close()
            
        mcgroup = "0.0.0.0"
        socket, group = bbmcast.mcast_sender(mcgroup)
        self.assertEquals(group, "<broadcast>")
        self.assertEquals(socket.getsockopt(SOL_SOCKET, SO_BROADCAST), 1)
        socket.close()

        mcgroup = "255.255.255.255"
        socket, group = bbmcast.mcast_sender(mcgroup)
        self.assertEquals(group, "<broadcast>")
        self.assertEquals(socket.getsockopt(SOL_SOCKET, SO_BROADCAST), 1)
        socket.close()

        mcgroup = (str(random.randint(0, 223)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)))
        self.assertRaises(IOError, bbmcast.mcast_sender, mcgroup)

        mcgroup = (str(random.randint(240, 255)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)))
        self.assertRaises(IOError, bbmcast.mcast_sender, mcgroup)

    def test_mcast_receiver(self):
        """Unit test for mcast_receiver.
        """
        mcport = random.randint(1025, 65535)
        mcgroup = "0.0.0.0"
        socket, group = bbmcast.mcast_receiver(mcport, mcgroup)
        self.assertEquals(group, "<broadcast>")
        socket.close()

        mcgroup = "255.255.255.255"
        socket, group = bbmcast.mcast_receiver(mcport, mcgroup)
        self.assertEquals(group, "<broadcast>")
        socket.close()

        # Valid multicast range is 224.0.0.0 to 239.255.255.255
        mcgroup = (str(random.randint(224, 239)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)))
        socket, group = bbmcast.mcast_receiver(mcport, mcgroup)
        self.assertEquals(group, mcgroup)
        socket.close()

        mcgroup = (str(random.randint(0, 223)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)))
        self.assertRaises(error, bbmcast.mcast_receiver, mcport, mcgroup)

        mcgroup = (str(random.randint(240, 255)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)) + "." +
                   str(random.randint(0, 255)))
        self.assertRaises(error, bbmcast.mcast_receiver, mcport, mcgroup)

if __name__ == "__main__":
    unittest.main()
