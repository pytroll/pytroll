import pytroll_db

dcm = pytroll_db.DCManager('postgresql://iceopr:Hot_Eyes@devsat-lucid:5432/testdb2')
#dcm = pytroll_db.DCManager('postgresql://a000680:@localhost.localdomain:5432/sat_db')

ft = dcm.get_file_type('HRPT')
ff = dcm.get_file_format('hrpt level 0')

nf = dcm.create_file('test2', ft, ff)

p = dcm.get_parameter('orbit_number')

pv = dcm.create_parameter_value(nf, p, 666)

value = 'LINESTRING (3 3, 4 4, 5 5, 6 6)'
import shapely
wkt_o = shapely.wkt.loads(value)
pls = dcm.create_parameter_linestring(nf, p, wkt_o)

dcm.save()
