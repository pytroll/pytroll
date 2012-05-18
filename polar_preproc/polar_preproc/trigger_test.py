#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012 Martin Raspaud

# Author(s):

#   Kristian Rune Larsen <krl@dmi.dk>
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

"""Trigger and region_collector test file
"""

from polar_preproc import trigger
from polar_preproc import region_collector
from pyresample import utils
import json
import os
from datetime import datetime, timedelta



input_dirs = ['tests/data',]

regions = [utils.load_area('tests/region_collector/areas.def', 'scan1')]

timeliness = timedelta(days=7)
collectors =  [region_collector.RegionCollector(region, timeliness) for region in regions]

# DONE timeout not handled
# DONE should be able to handle both inotify, database events or posttroll
# messages
# DONE metadata should be decoded.


def terminator(metadata):
    """Dummy terminator function.
    """
    print metadata

def read_granule_metadata(filename):
    """Read the json metadata from *filename*.
    """
    with open(filename) as jfp: 
        metadata =  json.load(jfp)[0]

    metadata['uri'] = "file://" + os.path.abspath(filename)

    for attr in ["start_time", "end_time"]:
        try:
            metadata[attr] = datetime.strptime(metadata[attr],
                                               "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            metadata[attr] = datetime.strptime(metadata[attr],
                                               "%Y-%m-%dT%H:%M:%S")
    return metadata

decoder = read_granule_metadata


granule_trigger = trigger.FileTrigger(collectors, terminator,
                                      decoder, input_dirs)

try:
    granule_trigger.loop()
except KeyboardInterrupt:
    print "Thank you for using pytroll! See you soon on pytroll.org."



