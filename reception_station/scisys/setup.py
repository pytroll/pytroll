#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012, 2013 Martin Raspaud

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

"""Setup for scisys reception system interface with pytroll.
"""


from setuptools import setup

setup(name="SMHI-SAF-scisys_receiver",
      version="0.2.2",
      description="Scisys message interface to pytroll",
      author='The pytroll team',
      author_email='martin.raspaud@smhi.se',
      #packages=['scisys_receiver'],
      scripts = ['bin/scisys_receiver.py'],
      data_files = [('/etc/init.d', ['etc/init.d/SMHI-scisys-receiver'])],
      zip_safe=False,
      license="GPLv3",
      install_requires=["posttroll"],
      extras_require={ 'daemon': ['python-daemon']},
      )
