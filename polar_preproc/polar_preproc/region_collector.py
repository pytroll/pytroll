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

"""
"""

import os
import time
from datetime import timedelta, datetime

import pyproj
from glob import glob

import numpy as np
from pyresample import geometry, utils
from pyorbital.orbital import Orbital
from polar_preproc.orbitno import get_tle

import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

PLOT = False


def corners(platform, start_time, end_time):
    """ Compute the corners of a satellite granule
    
        returns area (BaseDefinition)
    """
    tle = get_tle(platform, start_time)


    orbital = Orbital(tle.platform, line1=tle.line1, line2=tle.line2)
    track_start = orbital.get_lonlatalt(start_time)
    track_end = orbital.get_lonlatalt(end_time)

    geod = pyproj.Geod(ellps='WGS84')
    az_fwd, az_back, dist = geod.inv(track_start[0], track_start[1],
                                     track_end[0], track_end[1])

    del dist
    
    NPP_WIDTH = 3000000
    
    start_left = geod.fwd(track_start[0], track_start[1],
                          az_fwd - 90, NPP_WIDTH/2 )
    start_right = geod.fwd(track_start[0], track_start[1],
                           az_fwd + 90, NPP_WIDTH/2 )
    end_left = geod.fwd(track_end[0], track_end[1], az_back + 90, NPP_WIDTH/2 )
    end_right = geod.fwd(track_end[0], track_end[1], az_back - 90, NPP_WIDTH/2 )

    # Check in input data is within the region

    lons = np.array([[start_left[0], end_left[0]],
                     [start_right[0], end_right[0]]])
    lats = np.array([[start_left[1], end_left[1]],
                     [start_right[1], end_right[1]]])
    
    granule_area = geometry.SwathDefinition(lons, lats)
    return granule_area


class RegionCollector:
    """This is the region collector. It collects granules that overlap on a
    region of interest and return the collection of granules when it's done.
    
    """

    def __init__(self, region, 
                 timeliness=timedelta(seconds=600), 
                 granule_duration=None):
        self.region = region # area def
        self.granule_times = set()
        self.granules = []
        self.planned_granule_times = set()
        self.timeliness = timeliness
        self.timeout = None
        self.granule_duration = granule_duration

    def __call__(self, granule_metadata):
        return self.collect(granule_metadata)

    def collect(self, granule_metadata):
        """ 
            Parameters:

                granule_metadata : metadata 

        """ 

        # Check if input data is being waited for

        platform = granule_metadata['platform']
        start_time = granule_metadata['start_time']
        end_time = granule_metadata['end_time']


        if start_time in self.planned_granule_times:
            if PLOT:
                granule_area = corners(platform, start_time, end_time)

                lons2 = np.array((granule_area.lons[0, 0], granule_area.lons[0, 1],
                                  granule_area.lons[1, 1], granule_area.lons[1, 0], 
                                  granule_area.lons[0, 0]))
                lats2 = np.array((granule_area.lats[0, 0], granule_area.lats[0, 1], 
                                  granule_area.lats[1, 1], granule_area.lats[1, 0], 
                                  granule_area.lats[0, 0]))
                x, y = map(lons2.ravel(), lats2.ravel())
                map.plot(x, y, '-r')
            self.granule_times.add(start_time)
            self.granules.append(granule_metadata)
            # If last granule return swath and cleanup
            if self.granule_times == self.planned_granule_times:
                LOG.debug("Collection finished for area: " +
                          str(self.region.area_id))
                return self.finish()
            else:
                return

        # Get corners from input data

        if self.granule_duration is None:
            self.granule_duration = end_time - start_time
            LOG.info("Estimated granule duration to " + 
                     str(self.granule_duration))
        
        granule_area = corners(platform, start_time, end_time)

        if PLOT:
            lons2 = np.array((granule_area.lons[0, 0], granule_area.lons[0, 1],
                              granule_area.lons[1, 1], granule_area.lons[1, 0], 
                              granule_area.lons[0, 0]))
            lats2 = np.array((granule_area.lats[0, 0], granule_area.lats[0, 1], 
                              granule_area.lats[1, 1], granule_area.lats[1, 0], 
                              granule_area.lats[0, 0]))
            x, y = map(lons2.ravel(), lats2.ravel())

        # If file is within region, make pass prediction to know what to wait for

        if granule_area.overlaps(self.region):
            if PLOT:
                map.plot(x, y, '-r')
            self.granule_times.add(start_time)
            self.granules.append(granule_metadata)

            # Computation of the predicted granules within the region
            
            if not self.planned_granule_times:
                self.planned_granule_times.add(start_time)
                gr_time = start_time
                while True:
                    gr_time += self.granule_duration
                    gr_area = corners(platform, gr_time, 
                                      gr_time + self.granule_duration)
                    if not gr_area.overlaps(self.region):
                        break
                    self.planned_granule_times.add(gr_time)

                gr_time = start_time
                while True:
                    gr_time -= self.granule_duration
                    gr_area = corners(platform, gr_time, 
                                      gr_time + self.granule_duration)
                    if not gr_area.overlaps(self.region):
                        break
                    self.planned_granule_times.add(gr_time)

                LOG.debug("Planned granules: " + str(self.planned_granule_times))
                self.timeout = (max(self.planned_granule_times) 
                                + self.granule_duration
                                + self.timeliness)
                LOG.debug("Planned timeout: " + self.timeout.isoformat())

        else:
            if PLOT:
                map.plot(x, y, '-b')

        # If last granule return swath and cleanup
        if (self.granule_times and
            (self.granule_times == self.planned_granule_times)):
            LOG.debug("Collection finished for area: " +
                      str(self.region.area_id))
            return self.finish()
            
    def cleanup(self):
        self.granule_times = set()
        self.granules = []
        self.planned_granule_times = set()
        self.timeout = None

    def finish(self):
        granules = self.granules
        self.cleanup()
        return granules
        

def read_granule_metadata(filename):
    """ """
    import json
    with open(filename) as jfp: 
        metadata =  json.load(jfp)[0]

    metadata['uri'] = "file://" + os.path.abspath(filename)

    for attr in ["start_time", "end_time"]:
        try:
            metadata[attr] = datetime.strptime(metadata[attr], "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            metadata[attr] = datetime.strptime(metadata[attr], "%Y-%m-%dT%H:%M:%S")
    return metadata


if __name__ == '__main__':

    LOG.info("Welcome to pytroll")

    input_dir = "tests/data"

    region = utils.load_area('tests/region_collector/areas.def', 'scan1')
    LOG.debug("Read area " + str(region))

    NPP_GRANULE_DURATION = timedelta(seconds=85.75)

    time_diff = datetime.utcnow() - datetime(2012, 5, 14, 11, 48, 18)

    collector = RegionCollector(region, 
                                timeliness=time_diff + timedelta(seconds=5),
                                granule_duration=NPP_GRANULE_DURATION)
    old_granules = set()

        

    if PLOT:
        from mpl_toolkits.basemap import Basemap
        import matplotlib.pyplot as plt
        # set up orthographic map projection with
        # perspective of satellite looking down at 50N, 100W.
        # use low resolution coastlines.
        # don't plot features that are smaller than 1000 square km.
        map = Basemap(projection='nsper', lat_0 = 58, lon_0 = 16,
                      resolution = 'l', area_thresh = 1000.)
        # draw coastlines, country boundaries, fill continents.
        map.drawcoastlines()
        map.drawcountries()
        #map.fillcontinents(color = 'coral', lake_color="white")
        # draw the edge of the map projection region (the projection limb)
        map.drawmapboundary(fill_color='white')
        # draw lat/lon grid lines every 30 degrees.
        map.drawmeridians(np.arange(0, 360, 30))
        map.drawparallels(np.arange(-90, 90, 30))

        lons = [region.lons[0, 0], region.lons[0, -1], region.lons[-1, -1], region.lons[-1, 0], region.lons[0, 0]] 
        lats = [region.lats[0, 0], region.lats[0, -1], region.lats[-1, -1], region.lats[-1, 0], region.lats[0, 0]] 

        rx, ry = map(lons, lats)
        map.plot(rx, ry, "-g")
    
    try:
        while True:
       

            input_granules = set(glob(os.path.join(input_dir, "npp*.json")))

            input_granules -= old_granules

            swath = None

            for input_granule in sorted(list(input_granules)):
                metadata = read_granule_metadata(input_granule)
                swath = swath or collector.collect(metadata)
                old_granules.add(input_granule)

            if swath is not None:
                break
            
            if (collector.timeout is not None) and datetime.utcnow() > collector.timeout:
                LOG.info("Timeout! (" + collector.timeout.isoformat() + ")")
                swath = collector.granules 
                break

            time.sleep(1)

    except KeyboardInterrupt:
        pass


    print swath
    
    
    if PLOT:
        plt.show()
    
