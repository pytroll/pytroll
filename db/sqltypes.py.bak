import sqlalchemy

from shapely import geometry, wkb


class Geography(sqlalchemy.types.TypeEngine):
    """PostGIS Geometry Type."""

    def __init__(self, type_, dimension):
        super(Geography, self).__init__()
        self.SRID = 4326
        self.type = type_.upper()
        self.dimension = dimension

    def get_col_spec(self):
        return 'GEOGRAPHY'

    def process_bind_param(self, value, dialect):
        """Convert from Python type to database type."""
        
        """``value`` is a Python/Shapely geometry object."""
        if value is None:
            return None
        else:
            return 'SRID=%s;%s' % (self.SRID, value)
        

    def process_result_value(self, value, dialect):
        """Convert from database type to Python type."""
        
        """``value`` is a hex-encoded WKB string."""
        if value is None:
            return None
        else:
            return wkb.loads(value.decode('hex'))


class POINT(Geography):
    def __init__(self):
        super(POINT, self).__init__('POINT', 2)


class LINESTRING(Geography):
    def __init__(self):
        super(LINESTRING, self).__init__('LINESTRING', 2)


class MULTILINESTRING(Geography):
    def __init__(self):
        super(MULTILINESTRING, self).__init__('MULTILINESTRING', 2)


class MULTIPOLYGON(Geography):
    def __init__(self):
        super(MULTIPOLYGON, self).__init__('MULTIPOLYGON', 2)

class POLYGON(Geography):
    def __init__(self):
        super(POLYGON, self).__init__('POLYGON', 2)
