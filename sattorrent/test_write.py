#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012 SMHI

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

"""Continuous writing to test inotify
"""
from __future__ import with_statement 

import time
import os
import sys
from datetime import datetime

FILENAME = "20120130134606_NOAA_18.temp"

try:
    os.mkdir("/tmp/hrpt")
except OSError:
    pass

try:
    start_time = datetime.strptime(sys.argv[1], "%Y%m%d%H%M%S")
    if start_time > datetime.utcnow():
        time.sleep((start_time - datetime.utcnow()).seconds)
except IndexError:
    pass


with open(FILENAME, "rb") as fpr:
    with open("/tmp/hrpt/20120130134606_NOAA_18.temp", "wb") as fpw:
        truc = fpr.read(30)
        while truc:
            fpw.write(truc)
            truc = fpr.read(10024)
            time.sleep(0.166)
