import pytroll_db

dcm = pytroll_db.DCManager('postgresql://iceopr:Hot_Eyes@devsat-lucid:5432/testdb2')
#dcm = pytroll_db.DCManager('postgresql://a000680:@localhost.localdomain:5432/sat_db')

ft = dcm.get_file_type('HRPT')
ff = dcm.get_file_format('hrpt level 0')

nf = dcm.create_file('test100', file_type=ft, file_format=ff)


nf1 = dcm.create_file('test101', file_type_name='HRPT', file_format_name='hrpt level 0')
print nf
p = dcm.get_parameter('orbit_number')

pv = dcm.create_parameter_value(666, file_obj=nf, parameter=p)
pv = dcm.create_parameter_value(666, filename='test101', parameter_name='orbit_number')

value = 'LINESTRING (3 3, 4 4, 5 5, 6 6)'
import shapely
wkt_o = shapely.wkt.loads(value)
p_track = dcm.get_parameter('sub_satellite_track')
pls = dcm.create_parameter_linestring(wkt_o, file_obj=nf, parameter=p_track)
pls = dcm.create_parameter_linestring(wkt_o, filename="test100", parameter_name="sub_satellite_track")

#dcm.save()
