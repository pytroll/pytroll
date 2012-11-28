# Copyright (c) 2012
#

# Author(s): 
#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
Convert human coordinates to an area definition.

Here is a usage example:
python coord2area_def.py france stere 42.0 51.5 -5.5 8.0 1.5
(the arguments are "name proj min_lat max_lat min_lon max_lon resolution(km)")


and the result is:
REGION: france {
	NAME:	france
	PCS_ID:	stere_1.25_46.75
	PCS_DEF:	proj=stere,lat_0=46.75,lon_0=1.25,ellps=WGS84
	XSIZE:  746
	YSIZE:  703
	AREA_EXTENT:	(-559750.38109755167, -505020.6757764442,
559750.38109755167, 549517.35194826045)
};

"""

import sys
from pyproj import Proj

if len(sys.argv) != 8:
    print "Usage: ", sys.argv[0], "name proj min_lat max_lat min_lon max_lon resolution"
    exit(1)
    
name = sys.argv[1]
proj = sys.argv[2]

left = float(sys.argv[5])
right = float(sys.argv[6])
up = float(sys.argv[3])
down = float(sys.argv[4])

res = float(sys.argv[7]) * 1000

lat_0 = (up + down) / 2
lon_0 = (right + left) / 2

p = Proj(proj=proj, lat_0=lat_0, lon_0=lon_0, ellps="WGS84")

left_ex1, up_ex1 = p(left, up)
right_ex1, up_ex2 = p(right, up)
left_ex2, down_ex1 = p(left, down)
right_ex2, down_ex2 = p(right, down)

area_extent = (min(left_ex1, left_ex1),
               min(up_ex1, up_ex2),
               max(right_ex1, right_ex2),
               max(down_ex1, down_ex2))

xsize = int((area_extent[2] - area_extent[0]) / res)
ysize = int((area_extent[3] - area_extent[1]) / res)

print "REGION:", name, "{"
print "\tNAME:\t", name
print "\tPCS_ID:\t", proj + "_" + str(lon_0) + "_" + str(lat_0)
print ("\tPCS_DEF:\tproj=" + proj +
       ",lat_0=" + str(lat_0) +
       ",lon_0=" + str(lon_0) +
       ",ellps=WGS84")
print "\tXSIZE:\t", xsize
print "\tYSIZE:\t", ysize
print "\tAREA_EXTENT:\t", area_extent
print "};"


