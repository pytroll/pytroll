import pytroll_db

dcm = pytroll_db.DCManager('postgresql://iceopr:Hot_Eyes@devsat-lucid:5432/testdb2')

ft = dcm.get_file_type('HRPT')
ff = dcm.get_file_format('hrpt level 0')

nf = dcm.create_file('test', ft, ff)

p = dcm.get_parameter('orbit_number')

pv = dcm.create_parameter_value(nf, p, 666)

