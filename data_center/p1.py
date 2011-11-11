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

"""A very stupid consumer.
"""

from dc.subscriber import Subscriber
from posttroll.message_broadcaster import sendaddress
import socket

def get_own_ip():
    """Get the host's ip number.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(('smhi.se', 0))
    ip_ = sock.getsockname()[0]
    sock.close()
    return ip_

BROADCASTER_PORT = 21200
BROADCASTER = sendaddress('p1', (get_own_ip(), BROADCASTER_PORT), 2).start()

SUB = Subscriber("tcp://localhost:9000")

try:
    for msg in SUB(timeout=1):
        print "Consumer got", msg
        
except KeyboardInterrupt:
    print "terminating consumer..."
    SUB.close()
    BROADCASTER.stop()
