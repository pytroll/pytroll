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

"""A simple producer.
"""

import time

from posttroll.message import Message
from dc.connections import DCConnectionsPush

class Messager(object):
    """Dummy messager class.
    """
    def __init__(self):
        self.count = 0
    def __call__(self):
        self.count += 1        
        return Message('/test/1/2/3', 'info', "what's up doc #%d"%self.count)

if __name__ == '__main__':
    CONNECTIONS = DCConnectionsPush().start()
    MSG = Messager()
    while True:
        try:
            CONNECTIONS.send(MSG())
            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            print "quitting ..."
            CONNECTIONS.stop()
            break
