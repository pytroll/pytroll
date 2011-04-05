import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime,\
                       create_engine, ForeignKey, Table
#from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref, sessionmaker
from sqlalchemy.databases.postgres import PGBinary

#from osgeo import ogr
import shapely.wkb
import shapely.wkt

from sqltypes import LINESTRING

Base = declarative_base()

class Boundary(Base):
    __tablename__ = 'boundary'

    #mapping
    boundary_id = Column(Integer, primary_key=True)
    boundary_name = Column(String)
    boundary = Column(PGBinary)    
    creation_time = Column(DateTime)
    
    def __init__(self, boundary_id, boundary_name, boundary, creation_time):
        self.boundary_id = boundary_id
        self.boundary_name = boundary_name
        self.boundary = boundary
        self.creation_time = creation_time
        

class ParameterType(Base):
    __tablename__ = 'parameter_type'

    #mapping
    parameter_type_id = Column(Integer, primary_key=True)
    parameter_type_name = Column(String)
    parameter_location = Column(String)
    
    def __init__(self, parameter_type_id, parameter_type_name, parameter_location):
        self.parameter_type_id = parameter_type_id
        self.parameter_type_name = parameter_type_name
        self.parameter_location = parameter_location


class Parameter(Base):
    __tablename__ = 'parameter'

    #mapping
    parameter_id = Column(Integer, primary_key=True)
    parameter_type_id = Column(Integer)
    parameter_name = Column(String)
    description = Column(String)
    
    def __init__(self, parameter_id, parameter_type_id, parameter_name, description):
        self.parameter_id = parameter_id
        self.parameter_type_id = parameter_type_id
        self.parameter_name = parameter_name
        self.description = description

"""
class Tag(Base):
    __tablename__ = 'tag'

    #mapping
    tag_id = Column(Integer, primary_key=True)
    tag = Column(String)

    def __init__(self,):


class (Base):
    __tablename__ = ''

    #mapping
    
    def __init__(self,):

class (Base):
    __tablename__ = ''

    #mapping
    
    def __init__(self,):

class (Base):
    __tablename__ = ''

    #mapping
    
    def __init__(self,):

class (Base):
    __tablename__ = ''

    #mapping
    
    def __init__(self,):
"""


class ParameterLinestring(Base):
    __tablename__ = 'parameter_linestring'

    #mapping
    filename = Column(String, primary_key=True)
    parameter_id = Column(Integer, primary_key=True)
    creation_time = Column(DateTime)
    #data_value = Column(PGBinary)
    data_value = Column(LINESTRING())

    def __init__(self, filename, parameter_id, creation_time, data_value):
        self.filename = filename
        self.parameter_id = parameter_id
        self.creation_time = creation_time
        self.data_value = data_value




class ReportManager(object):

    def __init__(self, connection_string):
        engine = create_engine(connection_string)
        self._engine = engine
        Session = sessionmaker(bind=engine)
        self._session = Session()

    def get_param_track(self):
        #query = 'select filename, parameter_id from parameter_track';
        #data_proxy = self._engine.execute(query)
        #print data_proxy.fetchall()
        return  self._session.query(ParameterLinestring)

    def add_param_track(self):
        line_s = 'LINESTRING (3 1, 4 4, 5 5, 5 6)'
        wkt_o = shapely.wkt.loads(line_s)
        print wkt_o
        wkb_o = wkt_o.wkb #shapely.wkb.dumps(wkt_o)
        print type(wkb_o)

        print type(wkb_o)
        #param_track = ParameterLinestring("hrpt_201012011615_lvl0_smb.l0", 8, datetime.datetime.utcnow(), wkb_o.encode('hex'))
        param_track = ParameterLinestring("hrpt_201012011615_lvl0_smb.l0", 8, datetime.datetime.utcnow(), wkt_o)
        self._session.add(param_track)
        self._session.commit()

if __name__ == '__main__':
    rm = ReportManager('postgresql://iceopr:Hot_Eyes@devsat-lucid:5432/testdb2')
    pt = rm.get_param_track()
    res = pt.first()
    print type(res.data_value)
    #t_geo = ogr.CreateGeometryFromWkb(res.track.decode('hex'))
    #t_geo = shapely.wkb.loads(res.data_value.decode('hex')).wkt
    t_geo = res.data_value.wkt    

    print res.filename, res.parameter_id, res.creation_time, t_geo
    
    # insert into database
    rm.add_param_track()
    #pt = rm.get_param_track()
    #res = pt.first()
    
    





