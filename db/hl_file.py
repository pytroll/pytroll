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


import db.pytroll_db as db
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
import shapely
import numpy as np

def area_def2boundary(area_def, boundary_id):
    """Convert a pyresample *area_def* to a db Boundary object
    """


    lon_bound, lat_bound = area_def.get_boundary_lonlats()
    lons = np.concatenate((lon_bound.side1[:-1],
                           lon_bound.side2[:-1],
                           lon_bound.side3[:-1],
                           lon_bound.side4[:-1]))
    lats = np.concatenate((lat_bound.side1[:-1],
                           lat_bound.side2[:-1],
                           lat_bound.side3[:-1],
                           lat_bound.side4[:-1]))
    poly = shapely.geometry.asPolygon(np.vstack((lons, lats)).T)
    return db.Boundary(boundary_id, area_def.name, poly)


class File(object):

    def __init__(self, filename, dbm, filetype=None, fileformat=None):
        self.filename = filename
        self.dbm = dbm
        try:
            self._file = dbm.session.query(db.File).\
                         filter(db.File.filename==self.filename).one()
        except NoResultFound:
            self._file = self.dbm.create_file(self.filename,
                                              file_type_name=filetype,
                                              file_format_name=fileformat,
                                              creation_time=datetime.utcnow())
            self.dbm.session.commit()
            
    def add_bound(self, area_def):
        # find if the boundary is already there
        try:
            bound = self.dbm.session.query(db.Boundary).filter(db.Boundary.boundary_name == area_def.name).one()
        except NoResultFound:
            try:
                bid = self.dbm.session.query(db.Boundary).order_by(db.Boundary.boundary_id.desc()).first().boundary_id + 1
            except AttributeError:
                bid = 1        
            bound = area_def2boundary(area_def, bid)
            self.dbm.session.add(bound)
        self._file.boundary.append(bound)
        self.dbm.session.commit()

    def __setitem__(self, key, val):

        if key == "URIs":
            uris = self.dbm.session.query(db.FileURI).\
                   filter(db.FileURI.filename==self.filename).all()
            uri_vals = [i.uri for i in uris]

            # adding new uris
            for uri in val:
                if uri not in uri_vals:
                    self.dbm.create_file_uri(filename=self.filename, URI=uri)
            # deleting old uris
            for uri, uri_obj in zip(uri_vals, uris):
                if uri not in val:
                    self.dbm.session.delete(uri_obj)
                    
        elif key == "format":
            fileformat = self.dbm.get_file_format(val)
            self._file.file_format = fileformat

        elif key == "type":
            filetype = self.dbm.get_file_format(val)
            self._file.file_type = filetype

        elif key == "area":
            self.add_bound(val)

        elif key == "sub_satellite_track":
            value = 'LINESTRING ('
            for i, item in enumerate(val):
                if i == 0:
                    value += '%s %s' % (item[0], item[1])
                else:
                    value += ', %s %s' % (item[0], item[1])
            value += ')'

            wkt_o = shapely.wkt.loads(value)
            p_track = self.dbm.get_parameter('sub_satellite_track')
            try:
                self.dbm.session.query(db.ParameterLinestring).join(db.Parameter).filter(db.ParameterLinestring.filename==self.filename).filter(db.Parameter.parameter_name==key).one().data_value
            except NoResultFound:
                self.dbm.create_parameter_linestring(wkt_o,
                                                     filename=self.filename,
                                                     parameter=p_track)
            
        else:
            try:
                self.dbm.session.query(db.ParameterValue).join(db.Parameter).filter(db.ParameterValue.filename==self.filename).filter(db.Parameter.parameter_name==key).one().data_value
            except NoResultFound:
                self.dbm.create_parameter_value(filename=self.filename,
                                                parameter_name=key,
                                                data_value=val,
                                                creation_time=datetime.utcnow())
                
        self.dbm.session.commit()

    def __getitem__(self, key):

        if key == "URIs":
            return [i.uri for i in self.dbm.session.query(db.FileURI).filter(db.FileURI.filename==self.filename)]
        elif key == "type":
            return self._file.file_type.file_type_name
        elif key == "format":
            return self._file.file_format.file_format_name
        else:
            return self.dbm.session.query(db.ParameterValue).join(db.Parameter).filter(db.ParameterValue.filename==self.filename).filter(db.Parameter.parameter_name==key).one().data_value
            
