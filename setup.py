#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2011, 2012.

# Author(s):
 
#   The pytroll team

# This file is part of pytroll.

# Pytroll is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# mpop is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pytroll.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

setup(name="pytroll",
      version=0.1,
      description='Sandbox for pytroll',
      author='The pytroll team',
      author_email='team@pytroll.org',
      packages=['posttroll', 'np''],
      zip_safe=False,
      )
