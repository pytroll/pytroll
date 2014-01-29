import sqlalchemy

from shapely import geometry, wkb


DEFAULT_SRID = 4326

class Geography(sqlalchemy.types.TypeEngine):
    """PostGIS Geometry Type."""

    def __init__(self, type_, dimension, srid=DEFAULT_SRID):
        super(Geography, self).__init__()
        self.SRID = srid
        self.type = type_.upper()
        self.dimension = dimension
        
    def bind_processor(self, dialect):
        """Convert from Python type to database type."""
        def process(value):
            """``value`` is a Python/Shapely geometry object."""
            if value is None:
                return None
            else:
                return 'SRID=%s;%s' % (self.SRID, value)
        return process

    def result_processor(self, dialect, *args):
        """Convert from database type to Python type."""
        
        def process(value):
            """``value`` is a hex-encoded WKB string."""
            if value is None:
                return None
            else:
                return wkb.loads(value.decode('hex'))
        return process
    
    def get_col_spec(self):
        return 'GEOGRAPHY'

    
class POINT(Geography):
    def __init__(self, srid=DEFAULT_SRID):
        Geography.__init__(self, 'POINT', 2, srid)


class LINESTRING(Geography):
    def __init__(self, srid=DEFAULT_SRID):
        Geography.__init__(self, 'LINESTRING', 2, srid)


class MULTILINESTRING(Geography):
    def __init__(self, srid=DEFAULT_SRID):
        Geography.__init__(self, 'MULTILINESTRING', 2, srid)


class MULTIPOLYGON(Geography):
    def __init__(self, srid=DEFAULT_SRID):
        Geography.__init__(self, 'MULTIPOLYGON', 2, srid)

class POLYGON(Geography):
    def __init__(self, srid=DEFAULT_SRID):
        Geography.__init__(self, 'POLYGON', 2, srid)
