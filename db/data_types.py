#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012 Martin Raspaud

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

"""Adds the data types to the database.
"""


from db.pytroll_db import DCManager
dbm = DCManager('postgresql://polar:polar@localhost:5432/sat_db')
dbm.create_file_type(1, 'HRPT 0', 'HRPT level 0 data')
dbm.create_file_type(2, 'EOS 0', 'EOS level 0 data')
dbm.create_file_type(3, 'RDR', 'RDR data')
dbm.create_file_type(4, 'SDR', 'SDR data')

dbm.create_file_format(1, '16-bit HRPT Minor Frame', 'HRPT level 0 data')

dbm.create_parameter_type(1, "normal_parameter", "")

dbm.create_parameter(1, 1, "start_time", "")
dbm.create_parameter(2, 1, "end_time", "")
dbm.create_parameter(3, 1, "orbit number", "")
dbm.create_parameter(4, 1, "risetime", "")
dbm.create_parameter(5, 1, "falltime", "")
dbm.create_parameter(6, 1, "satellite", "")
dbm.create_parameter(7, 1, "format", "")
dbm.create_parameter(8, 1, "type", "")
dbm.create_parameter(9, 1, "uri", "")



dbm.session.commit()
