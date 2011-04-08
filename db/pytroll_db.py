import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime,\
                       create_engine, ForeignKey, Table

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation, backref, sessionmaker

#from osgeo import ogr
import shapely.wkb
import shapely.wkt

from sqltypes import LINESTRING, POLYGON

Base = declarative_base()

#relation table
data_boundary = Table('data_boundary', Base.metadata,\
                      Column('filename', String,\
                             ForeignKey('file.filename')),\
                      Column('boundary_id', Integer,\
                             ForeignKey('boundary.boundary_id')))

#relation table
file_type_parameter = Table('file_type_parameter', Base.metadata,\
                      Column('file_type_id', Integer,\
                             ForeignKey('file_type.file_type_id')),\
                      Column('parameter_id', Integer,\
                             ForeignKey('parameter.parameter_id')))

#relation table
file_tag = Table('file_tag', Base.metadata,\
                      Column('tag_id', Integer,\
                             ForeignKey('tag.tag_id')),\
                      Column('filename', String,\
                             ForeignKey('file.filename')))

#relation table
file_type_tag = Table('file_type_tag', Base.metadata,\
                      Column('tag_id', Integer,\
                             ForeignKey('tag.tag_id')),\
                      Column('file_type_id', Integer,\
                             ForeignKey('file_type.file_type_id')))

        

class ParameterType(Base):
    """Mapping the DB-table parameter_type to a python object
    """ 
    __tablename__ = 'parameter_type'

    #mapping
    parameter_type_id = Column(Integer, primary_key=True)
    parameter_type_name = Column(String)
    parameter_location = Column(String)    

    def __init__(self, parameter_type, parameter_type_name, parameter_location):
        self.parameter_type = parameter_type
        self.parameter_type_name = parameter_type_name
        self.parameter_location = parameter_location


class Parameter(Base):
    __tablename__ = 'parameter'

    #mapping
    parameter_id = Column(Integer, primary_key=True)
    parameter_type_id = Column(Integer, ForeignKey('parameter_type.parameter_type_id'))
    parameter_name = Column(String)
    description = Column(String)
    
    def __init__(self, parameter_id, parameter_type_id, parameter_name, description):
        self.parameter_id = parameter_id
        self.parameter_type_id = parameter_type_id
        self.parameter_name = parameter_name
        self.description = description


class Tag(Base):
    __tablename__ = 'tag'

    #mapping
    tag_id = Column(Integer, primary_key=True)
    tag = Column(String)

    def __init__(self,tag_id, tag):
        self.tag_id = tag_id
        self.tag = tag


class FileFormat(Base):
    __tablename__ = 'file_format'

    #mapping
    file_format_id = Column(Integer, primary_key=True)
    file_format_name = Column(String)
    description = Column(String)
    
    def __init__(self,file_format_id, file_format_name, description):
        self.file_format_id = file_format_id
        self.file_format_name = file_format_name
        self.description = description



class FileType(Base):
    __tablename__ = 'file_type'

    #mapping
    file_type_id = Column(Integer, primary_key=True)
    file_type_name = Column(String)
    description = Column(String)

    def __init__(self, file_type_id, file_type_name, description):
        self.file_type_id = file_type_id
        self.file_type_name = file_type_name
        self.description = description


class File(Base):
    __tablename__ = 'file'

    #mapping
    filename = Column(String, primary_key=True)
    file_type_id = Column(Integer, ForeignKey('file_type.file_type_id'))
    file_format_id = Column(Integer, ForeignKey('file_format.file_format_id'))
    is_archived = Column(Boolean)
    creation_time = Column(DateTime)
    
    def __init__(self, filename, file_type, file_format, is_archived, creation_time):
        self.filename = filename
        self.file_type = file_type
        self.file_format = file_format
        self.is_archived = is_archived
        self.creation_time = creation_time


class Boundary(Base):
    __tablename__ = 'boundary'

    #mapping
    boundary_id = Column(Integer, primary_key=True)
    boundary_name = Column(String)
    boundary = Column(POLYGON())    
    creation_time = Column(DateTime)
    
    def __init__(self, boundary_id, boundary_name, boundary, creation_time=None):
        self.boundary_id = boundary_id
        self.boundary_name = boundary_name
        self.boundary = boundary
        if creation_time is None:
            creation_time = datetime.datetime.utcnow()
        self.creation_time = creation_time


class ParameterLinestring(Base):
    __tablename__ = 'parameter_linestring'

    #mapping
    filename = Column(String, ForeignKey('file.filename'), primary_key=True)
    parameter_id = Column(Integer, ForeignKey('parameter.parameter_id'), primary_key=True)
    creation_time = Column(DateTime)
    data_value = Column(LINESTRING())

    def __init__(self, file_obj, parameter, data_value, creation_time):
        self.file_obj = file_obj
        self.parameter = parameter
        self.creation_time = creation_time
        self.data_value = data_value


class ParameterValue(Base):
    __tablename__ = "parameter_value"

    #mapping
    filename = Column(String, ForeignKey('file.filename'), primary_key=True)
    parameter_id = Column(Integer, ForeignKey('parameter.parameter_id'), primary_key=True)
    data_value = Column(String)
    creation_time = Column(DateTime)

    def __init__(self, file_obj, parameter, data_value, creation_time):
        self.file_obj = file_obj
        self.parameter = parameter
        self.creation_time = creation_time
        self.data_value = data_value


class FileURI(Base):
    __tablename__ = "file_uri"

    #mapping
    file_type_id = Column(Integer, ForeignKey('file_type.file_type_id'), primary_key=True)
    file_format_id = Column(Integer, ForeignKey('file_format.file_format_id'), primary_key=True)
    sequence = Column(Integer, primary_key=True)
    uri = Column(String, primary_key=True)
    
    def __init__(self, file_type, file_format, sequence, uri):
        self.file_type = file_type
        self.file_format = file_format
        self.sequence = sequence
        self.uri = uri


#
#Relations

#ParameterType
ParameterType.parameters = relation(Parameter, backref='parameter_type')

#Parameter
Parameter.parameter_values = relation(ParameterValue, backref='parameter')
Parameter.parameter_linestrings = relation(ParameterLinestring, backref='parameter')

#FileFormat
FileFormat.file_uris = relation(FileURI, backref='file_format')
FileFormat.file_objs = relation(File, backref='file_format')

#FileType
FileType.parameters = relation(Parameter, secondary=file_type_parameter, backref='file_types')
FileType.file_uris = relation(FileURI, backref='file_type')
FileType.file_objs = relation(File, backref='file_type')
FileType.file_type_tags = relation(Tag, secondary=file_type_tag, backref='file_types')


#File
File.parameter_values = relation(ParameterValue, backref='file_obj')
File.parameter_linestrings = relation(ParameterLinestring, backref='file_obj')
File.file_tags = relation(Tag, secondary=file_tag, backref='file_objs')
File.boundary = relation(Boundary, secondary=data_boundary, backref='file_objs')


class DCManager(object):
    """Data Center Manager
    """

    def __init__(self, connection_string):
        engine = create_engine(connection_string)
        self._engine = engine
        Session = sessionmaker(bind=engine)
        self._session = Session()

    @property
    def engine(self):
        return self._engine 

    @property
    def session(self):
        return self._session

    def save(self):
        try:
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def rollback(self):
        self._session.rollback()

    def create_file_type(self, file_type_id, file_type_name, description):
        file_type = FileType(file_type_id, file_type_name, description)
        self._session.add(file_type)
        return file_type

    def create_file_format(self, file_format_id, file_format_name, description):
        file_format = FileFormat(file_format_id, file_format_name, description)
        self._session.add(file_format)
        return file_format

    def create_file_uri(self, file_type, file_format, URI, sequence=1):
        file_uri = FileURI(file_type, file_format, URI, sequence)
        self._session.add(file_uri)
        return file_uri

    def create_parameter_type(self, parameter_type_id, parameter_type_name, parameter_location):
        parameter_type = ParameterType(parameter_type_id, parameter_type_name, parameter_location)
        self._session.add(parameter_type)
        return parameter_type

    def create_parameter(self, parameter_id, parameter_type, parameter_name, description):
        parameter = Parameter(parameter_id, parameter_type, parameter_name, description)
        self._session.add(parameter)
        return parameter

    def create_file_type_parameter(self, **kwargs):
        """ Creates a relation between a filetype and a parameter

            Parameters : 
                file_type : FileType object
                file_type_name : str
                        FileType object name
                parameters : list
                        list of Parameter objects
                parameter_names : list
                        list of Parameter object names

            Returns:
                FileType object with new relations

        Notice : 
            Either file_type or file_type_name must be provided
            Either parameters or parameter_names must be provided
        """

        if 'file_type' in kwargs:
            file_type = kwargs['file_type']
        elif 'file_type_name' in kwargs:
            file_type = self.get_file_type(kwargs['file_type_name'])
        else:
            raise TypeError("No FileType reference defined")
        
        if 'parameters' in kwargs:
            for param in kwargs['parameters']:
                file_type.parameters.append(param)
        elif 'parameter_names' in kwargs:
            for parameter_name in kwargs['parameter_names']:
                parameter = self.get_parameter(parameter_name)
                file_type.parameters.append(parameter)
        else:
            raise TypeError("No FileType reference defined")
        
        return file_type

    def create_parameter_value(self, data_value, **kwargs):
        """Creates a ParameterValue object from a data value and File and
        Parameter references.

            Parameters :
                data_value :
                    data value corresponding to parameter type
                file_obj : File object
                filename : str
                    File object name
                parameter : Parameter object
                parameter_name : str
                    Parameter name
                creation_time : datetime object
                    Time of creation

                Returns : 
                    ParameterValue Object

        Notice : 
            Either file_obj or filename must be provided
            Either parameter or parameter_name must be provided

        """
        
        creation_time = datetime.datetime.utcnow()
        if 'creation_time' in kwargs:
            creation_time = kwargs['creation_time']

        if 'file_obj' in kwargs:
            file_obj = kwargs['file_obj']
        elif 'filename' in kwargs:
            file_obj = self.get_file(kwargs['filename'])
        else:
            raise TypeError("No file reference defined")

        if 'parameter' in kwargs:
            parameter = kwargs['parameter']
        elif 'parameter_name' in kwargs:
            parameter = self.get_parameter(kwargs['parameter_name'])
        else:
            raise TypeError("No parameter reference defined")

        parameter_value = ParameterValue(file_obj, parameter, data_value, creation_time)         
        self._session.add(parameter_value)
        return parameter_value

    def create_parameter_linestring(self, linestring, **kwargs):
        """Creates a ParameterLinestring object from a linestring and File and
        Parameter references.

            Parameters:
                linestring : shapely linestring object
                file_obj : File object
                filename : str
                    File object name
                parameter : Parameter object
                parameter_name : str
                    Parameter name
                creation_time : datetime object
                    Time of creation

                Returns : 
                    ParameterLinestring Object

        Notice : 
            Either file_obj or filename must be provided
            Either parameter or parameter_name must be provided

        """
        
        creation_time = datetime.datetime.utcnow()
        if 'creation_time' in kwargs:
            creation_time = kwargs['creation_time']

        if 'file_obj' in kwargs:
            file_obj = kwargs['file_obj']
        elif 'filename' in kwargs:
            file_obj = self.get_file(kwargs['filename'])
        else:
            raise TypeError("No file reference defined")

        if 'parameter' in kwargs:
            parameter = kwargs['parameter']
        elif 'parameter_name' in kwargs:
            parameter = self.get_parameter(kwargs['parameter_name'])
        else:
            raise TypeError("No parameter reference defined")

        parameter_linestring = ParameterLinestring(file_obj, parameter, linestring, creation_time)         
        self._session.add(parameter_linestring)
        return parameter_linestring

    def create_boundary(self, boundary_id, boundary_name, boundary, creation_time=None):
        if creation_time is None:
            creation_time = datetime.datetime.utcnow()
        boundary_obj = Boundary(boundary_id, boundary_name, boundary, creation_time)         
        self._session.add(boundary_obj)
        return boundary_obj

    def create_tag(self, tag_id, tag):
        tag_obj = Tag(tag_id, tag)
        self._session.add(tag_obj)
        return tag_obj

    def get_file_type(self, file_type_name):
        return self._session.query(FileType).\
               filter(FileType.file_type_name == file_type_name).one()

    def get_file_format(self, file_format_name):
        return self._session.query(FileFormat).\
               filter(FileFormat.file_format_name == file_format_name).one()

    def get_parameter(self, parameter_name):
        return self._session.query(Parameter).\
               filter(Parameter.parameter_name == parameter_name).one()

    def get_file(self, filename):
        return self._session.query(File).\
               filter(File.filename == filename).one()

    def create_file(self, filename, **kwargs):
        """Creates a File object from a file name and FileType and
        FileFormat references.

            Parameters:
                data_value :
                    data value corresponding to parameter type
                file_type : FileType object
                file_type_id : int
                    FileType object id
                file_type_name : str
                    FileType object name
                file_format : FileFormat object
                file_format_id : int
                    FileFormat object id
                file_format_name : str
                    FileFormat object name
                creation_time : datetime object
                    Time of creation
                is_archived : boolean
                    if file is archived

                Returns : 
                    File Object

        Notice : 
            Either file_type or file_type_id or file_type_name must be provided
            Either file_format or file_format_id or file_format_name must be provided

        """
        

        is_archived = False
        if 'is_archived' in kwargs:
            is_archived = kwargs['is_archived']

        creation_time = datetime.datetime.utcnow()
        if 'creation_time' in kwargs:
            creation_time = kwargs['creation_time']
        
        if 'file_type' in kwargs:
            file_type = kwargs['file_type']
        elif 'file_type_id' in kwargs:
            file_type = self._session.query(FileType).\
                filter(FileType.file_type_id == kwargs['file_type_id']).one()
        elif 'file_type_name' in kwargs:
            file_type = self.get_file_type(kwargs['file_type_name']) 
        else:
            raise TypeError("file_type not defined") 

        if 'file_format' in kwargs:
            file_format = kwargs['file_format']
        elif 'file_format_id' in kwargs:
            file_format = self._session.query(FileFormat).\
                filter(FileFormat.file_format_id == kwargs['file_format_id']).one()
        elif 'file_format_name' in kwargs:
            file_format = self.get_file_format(kwargs['file_format_name'])
        else:
            raise TypeError("file_format not defined") 

        file_obj = File(filename,file_type, file_format, is_archived, creation_time)
        
        self._session.add(file_obj)
        return file_obj



if __name__ == '__main__':
    rm = DCManager('postgresql://iceopr@devsat-lucid:5432/testdb2')
    #rm = DCManager('postgresql://a000680:@localhost.localdomain:5432/sat_db')

    f = rm.get_file()
    pl = f.parameter_linestrings[0]
    print type(pl.data_value)
    print pl.data_value.wkt
    
