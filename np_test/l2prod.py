#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012, 2014.

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

from posttroll.subscriber import Subscribe
from posttroll.publisher import Publish
from posttroll.message import Message

import logging
from logger import PytrollFormatter, PytrollHandler

logger = logging.getLogger("hrpt2")
logger.setLevel(logging.DEBUG)

try:
    with Publish("l2prod", 0, ["HRPT/2"]) as pub:
        ch = PytrollHandler(pub)
        ch.setLevel(logging.DEBUG)
        formatter = PytrollFormatter("/oper/polar/gds")
        ch.setFormatter(formatter)
        # add ch to logger
        logger.addHandler(ch)
        with Subscribe("HRPT/1b", "EOS/1") as sub1:
            for msg in sub1.recv():
                
                ##data = msg.data
                ##if data["type"] != "HRPT 1b":
                ##    continue

                logger.error("hej")

                
                print "Consumer got", msg
                if msg is not None and msg.type == "file":
                    data = msg.data
                    data["type"] = "HRPT 2"
                    data["format"] = "Pytroll's netcdf"
                    print "publishing", Message('/dc/polar/gds', "file",
                                                data).encode()
                    pub.send(Message('/dc/polar/gds', "file",
                                         data).encode())
except KeyboardInterrupt:
    print "terminating consumer..."

