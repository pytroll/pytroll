#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Martin Raspaud

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

"""our own schedule !
"""

from datetime import datetime, timedelta
from pyorbital import orbital
import numpy as np
from scipy.optimize import brentq

FORWARD = 6


class Pass(object):
    """A pass.
    """

    buffer = timedelta(minutes=2)
    
    def __init__(self, satellite, risetime, falltime, number=0):
        """
        
        Arguments:
        - `satellite`:
        - `risetime`:
        - `falltime`:
        """
        self._satellite = satellite
        self.risetime = risetime
        self.falltime = falltime
        self._number = number
        
    def overlaps(self, other):
        """Check if two passes overlap.
        """
        return (self.risetime < other.falltime + self.buffer and
                self.falltime + self.buffer > other.risetime)

    def __cmp__(self, other):
        if self.risetime < other.risetime:
            return -1
        if self.risetime > other.risetime:
            return 1
        else:
            return 0

    def __eq__(self, other):
        return (self.risetime == other.risetime and
                self.falltime == other.falltime and
                self._satellite == other._satellite)

    def __repr__(self):
        return self._satellite + ": " + self.risetime.isoformat() + " " + self.falltime.isoformat()
        #return str(self._number)

def group_overlaps(self, other):
    for p1 in self:
        for p2 in other:
            if p1.overlaps(p2):
                return True
    return False
    
def get_next_passes(satellite, start_time, length, lon, lat, alt):
    """length in hours
    *lon*, *lat*, *alt* of the receiving station.
    """    
    o = orbital.Orbital(satellite=satellite)
    def elevation(minutes):
        return o.get_observer_look(start_time + timedelta(minutes=minutes),
                                   lon, lat, alt)[1]

    arr = np.array([elevation(m) for m in range(length * 60)])
    a = np.where(np.diff(np.sign(arr)))[0]

    res = []
    risetime = None
    falltime = None

    for guess in a:
        horizon_time = start_time + timedelta(minutes=brentq(elevation,
                                                             guess, guess + 1))
        if arr[guess] < 0:
            risetime = horizon_time
            falltime = None
        else:
            falltime = horizon_time
            if risetime:
                res += [Pass(satellite, risetime, falltime)]
            risetime = None
    return res
                
  
utctime = datetime.utcnow()

satellites = ["noaa 19", "noaa 18", "noaa 16", "noaa 15", "metop-a", "metop-b", "terra", "aqua", "suomi npp"]

passes = {}


passes["noaa 19"] = [Pass("noaa 19", datetime(2013, 2, 6, 10, 0), datetime(2013, 2, 6, 10, 20), 1),
                     Pass("noaa 19", datetime(2013, 2, 6, 10, 34), datetime(2013, 2, 6, 11, 55), 2)]

passes["noaa 18"] = [Pass("noaa 18", datetime(2013, 2, 6, 10, 15), datetime(2013, 2, 6, 10, 30), 3),
                     Pass("noaa 18", datetime(2013, 2, 6, 11, 59), datetime(2013, 2, 6, 12, 13), 4)]

passes["suomi npp"] = [Pass("suomi npp", datetime(2013, 2, 6, 10, 15), datetime(2013, 2, 6, 10, 35), 5),
                       Pass("suomi npp", datetime(2013, 2, 6, 11, 54), datetime(2013, 2, 6, 12, 15), 6)]

passes["noaa 16"] = [Pass("noaa 16", datetime(2013, 2, 6, 12, 50), datetime(2013, 2, 6, 13, 10), 7),
                     Pass("noaa 16", datetime(2013, 2, 6, 14, 10), datetime(2013, 2, 6, 14, 30), 8)]

passes = {}
for sat in satellites:
    passes[sat] = get_next_passes(sat, utctime, FORWARD, 16, 58, 0.05)


granularity = timedelta(minutes=60)

import operator
allpasses = set(reduce(operator.concat, passes.values()))

for passage in sorted(allpasses):
    print passage

from copy import copy


import numpy as np

def conflicting_passes(allpasses):


    passes = list(allpasses)
    passes.sort()

    last_time = None
    group = []
    groups = []
    for passage in passes:
        if last_time is None:
            last_time = passage.falltime
            group.append(passage)
            continue
        if passage.risetime < last_time:
            group.append(passage)
            if last_time < passage.falltime:
                last_time = passage.falltime

        else:
            groups.append(group)
            group = [passage]
            last_time = passage.falltime

    groups.append(group)
    return groups

def get_graph(passes):
    """Get the different non-conflicting solutions in a group of conflicting
    passes.
    """
    # Uses graphs and maximal clique finding with the Bron-Kerbosch algorithm.

    order = len(passes)

    if order == 1:
        return [passes]

    adj_matrix = np.zeros((order, order), dtype=np.int8)

    for i, passage in enumerate(passes):
        for j in range(i + 1, order):
            overlaps = not passage.overlaps(passes[j])
            adj_matrix[i, j] = overlaps
            adj_matrix[j, i] = overlaps

    graph = Graph(adj_matrix)
    groups = []
    for res in graph.bron_kerbosch(set(), set(graph.vertices), set()):
        grp = []
        for v in res:
            grp.append(passes[v])
        groups.append(grp)

    return groups


class Graph(object):

    def __init__(self, adj_matrix):
        self.order = adj_matrix.shape[0]
        self.vertices = np.arange(self.order)
        self.adj_matrix = adj_matrix

    def neighbours(self, v):
        return self.vertices[self.adj_matrix[v, :] == 1]
        
    def bron_kerbosch(self, r, p, x):
        if len(p) == 0 and len(x) == 0:
            yield r
        for v in p:
            for res in self.bron_kerbosch(r | set((v, )),
                                          p & set(self.neighbours(v)),
                                          x & set(self.neighbours(v))):
                yield res
            p = p - set((v, ))
            x = x | set((v, ))

def duration(passage):
    """Get the score of a passage depending of its duration.
    """
    return (passage.falltime - passage.risetime).seconds

def area_coverage(passage):
    """Get the score depending on the coverage of the area of interest.
    """
    from pyorbital import orbital, astronomy, geoloc, geoloc_instrument_definitions

    o = orbital.Orbital(satellite=passage._satellite)

    scans_nb = np.ceil(((passage.falltime - passage.risetime).seconds +
                        (passage.falltime - passage.risetime).microseconds / 1000000.0) * 6)

    sgeom = geoloc_instrument_definitions.avhrr(scans_nb, np.array([0, 2047]))

    s_times = sgeom.times(passage.risetime)
    pixel_pos = geoloc.compute_pixels((o.tle._line1, o.tle._line2), sgeom, s_times, (0, 0, 0))
    pos_time = geoloc.get_lonlatalt(pixel_pos, s_times)

    
    
def day(passage):
    """Get the score depending on the day percentage.
    """
    print passage
    
    from pyorbital import orbital, astronomy, geoloc, geoloc_instrument_definitions

    o = orbital.Orbital(satellite=passage._satellite)
    scans_nb = np.ceil(((passage.falltime - passage.risetime).seconds +
                        (passage.falltime - passage.risetime).microseconds / 1000000.0) * 6)

    sgeom = geoloc_instrument_definitions.avhrr(scans_nb, np.array([0, 2047]))
    
    s_times = sgeom.times(passage.risetime)
    pixel_pos = geoloc.compute_pixels((o.tle._line1, o.tle._line2), sgeom, s_times, (0, 0, 0))
    pos_time = geoloc.get_lonlatalt(pixel_pos, s_times)

    sides = astronomy.cos_zen(s_times, pos_time[0], pos_time[1]).reshape((scans_nb, 2))

    scans_nb = 1
    sgeom = geoloc_instrument_definitions.avhrr(scans_nb, np.arange(2048))

    s_times = sgeom.times(passage.risetime)
    pixel_pos = geoloc.compute_pixels((o.tle._line1, o.tle._line2), sgeom, s_times, (0, 0, 0))
    pos_time = geoloc.get_lonlatalt(pixel_pos, s_times)
    bottom = astronomy.cos_zen(s_times, pos_time[0], pos_time[1])

    s_times = sgeom.times(passage.falltime)
    pixel_pos = geoloc.compute_pixels((o.tle._line1, o.tle._line2), sgeom, s_times, (0, 0, 0))
    pos_time = geoloc.get_lonlatalt(pixel_pos, s_times)
    top = astronomy.cos_zen(s_times, pos_time[0], pos_time[1])
    
    

def argmax(iterable):
    return max((x, i) for i, x in enumerate(iterable))[1]

def get_max(groups, fun):
    """Get the best group of *groups* using the score function *fun*
    """
    scores = []
    for grp in groups:
        scores.append(sum([fun(p) for p in grp]))
    return groups[argmax(scores)]
            
        
#grs = conflicting_passes(allpasses)

#sched = []

#for gr in grs:
#    sched.extend(get_max(get_graph(gr), duration))

#from pprint import pprint

#pprint(sched)

day(list(allpasses)[10])



# # how far in the future ?
# sch_length = FORWARD

# o = orbital.Orbital(satellite="noaa 19")

# utctime = datetime.utcnow()

# def elevation(minutes):
#     return o.get_observer_look(utctime + timedelta(minutes=minutes), 16.0, 58.0, 0.05)[1]

# arr = np.array([elevation(m) for m in range(sch_length * 60)])
# a = np.where(np.diff(np.sign(arr)))[0]

# print "risetime\t\t\tfalltime"

# risetime = None

# for guess in a:
#     horizon_time = utctime + timedelta(minutes=brentq(elevation,
#                                                       guess, guess + 1))
#     if arr[guess] < 0:
#         risetime = horizon_time
#     else:
#         falltime = horizon_time
#         if risetime:
#             print risetime.isoformat(), "\t", falltime.isoformat()
