#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010-2012.

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


import pytroll_db as db
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
import shapely

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
            self.dbm.create_parameter_linestring(wkt_o,
                                                 filename=self.filename,
                                                 parameter=p_track)
            
        else:
            try:
                self.dbm.session.query(db.ParameterValue).join(db.Parameter).filter(db.ParameterValue.filename==self.filename).filter(db.Parameter.parameter_name==key).one().data_value = val
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
            
