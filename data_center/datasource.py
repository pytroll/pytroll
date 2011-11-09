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

"""A dummy datasource, sends messages.
"""

import time

from posttroll.message import Message
from dc.publisher import Publisher



class Messager(object):
    """Dummy messager class.
    """
    def __init__(self):
        self.count = 0
    def __call__(self):
        self.count += 1
        metadata = {}
        metadata['format'] = "ascii"
        metadata['uri'] = 'file:///tmp/dummy' + str(self.count)
        return Message('/dummy_l0', 'file', metadata)

if __name__ == '__main__':
    PUB = Publisher("tcp://lo:9000")
    MSG = Messager()
    while True:
        try:
            PUB.send(str(MSG()))
            time.sleep(2)
        except (KeyboardInterrupt, SystemExit):
            print "quitting ..."
            PUB.stop()
            break
