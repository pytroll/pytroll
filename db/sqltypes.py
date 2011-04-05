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

    def bind_processor(self, dialect):
        """Convert from Python type to database type."""
        def process(value):
            """``value`` is a Python/Shapely geometry object."""
            if value is None:
                return None
            else:
                return 'SRID=%s;%s' % (self.SRID, value)
        return process

    def result_processor(self, dialect):
        """Convert from database type to Python type."""
        def process(value):
            """``value`` is a hex-encoded WKB string."""
            if value is None:
                return None
            else:
                return wkb.loads(value.decode('hex'))
        return process


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
