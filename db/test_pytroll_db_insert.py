#!/usr/bin/env python
#
#
#
# 

from datetime import datetime
import pytroll_db as db 

"""Insert test values into database through SQLAlchemy interface """


dcm = db.DCManager('postgresql://a001673:@localhost.localdomain:5432/sat_db')

hrpt = dcm.create_file_type(1, 'HRPT', 'HRPT level 0 data')
hirlam = dcm.create_file_type(2, 'smhi_hirlam', 'HIRLAM data')
#dcm.create_file_type(3, "HRIT", "met 9 hrit data")

hrpt_L0 = dcm.create_file_format(1, 'hrpt level 0', '')
grib = dcm.create_file_format(2, 'GRIB', '')


dcm.create_parameter_type(1, 'dummy', 'parameter_value')

dcm.create_parameter(1, 1, 'time_of_first_scanline', '')
dcm.create_parameter(2, 1, 'time_of_last_scanline', '')
dcm.create_parameter(3, 1, 'orbit_number', '')
dcm.create_parameter(4, 1, 'satellite_name', '')
dcm.create_parameter(5, 1, 'time_of_analysis', '')
dcm.create_parameter(6, 1, 'forcast_length', '')
dcm.create_parameter(7, 1, 'processing_center', '')
dcm.create_parameter(8, 1, 'sub_satellite_track', '')

dcm.create_file_type_parameter(1, 1)
dcm.create_file_type_parameter(1, 2)
dcm.create_file_type_parameter(1, 3)
dcm.create_file_type_parameter(1, 4)
dcm.create_file_type_parameter(1, 8)
dcm.create_file_type_parameter(2, 5)
dcm.create_file_type_parameter(2, 6)
dcm.create_file_type_parameter(2, 7)

dcm.create_file('hrpt_201012011615_lvl0_smb.l0',
                file_type=hrpt,
                file_format=hrpt_L0,
                is_archived=False,
                creation_time=datetime(2010, 12, 1, 16, 15))
dcm.create_file('hrpt_201012011715_lvl0_smb.l0',
                file_type=hrpt,
                file_format=hrpt_L0,
                is_archived=False,
                creation_time=datetime(2010, 12, 1, 17, 10))
dcm.create_file('hrpt_201012011815_lvl0_smb.l0',
                file_type=hrpt,
                file_format=hrpt_L0,
                is_archived=False,
                creation_time=datetime(2010, 12, 1, 18, 10))
dcm.create_file('hirlam_2010_12_01_1200_areaB.grib',
                file_type=hirlam,
                file_format=grib,
                is_archived=False,
                creation_time=datetime(2010, 12, 1, 12, 07))


dcm.create_parameter_value('hrpt_201012011615_lvl0_smb.l0', 1, '2010-12-01 15:55:00', '2010-12-01 16:15:00')

dcm.create_parameter_value('hrpt_201012011615_lvl0_smb.l0', 2, '2010-12-01 16:10:00', '2010-12-01 16:15:00')
dcm.create_parameter_value('hrpt_201012011615_lvl0_smb.l0', 3, '2134', '2010-12-01 16:15:00')
dcm.create_parameter_value('hrpt_201012011615_lvl0_smb.l0', 4, '19', '2010-12-01 16:15:00')
dcm.create_parameter_value('hirlam_2010_12_01_1200_areaB.grib', 5, '2010-12-01 12:00:00', '2010-12-01 16:15:00')
dcm.create_parameter_value('hirlam_2010_12_01_1200_areaB.grib', 6, '6', '2010-12-01 16:15:00')
dcm.create_parameter_value('hirlam_2010_12_01_1200_areaB.grib', 7, '82', '2010-12-01 16:15:00')

dcm.create_parameter_linestring('hrpt_201012011615_lvl0_smb.l0', 8, 'LINESTRING(0 47.606, 3 51.5, 5 56, 10 59, 15 66)'::geography, '2010-12-01 16:10:00')
dcm.create_parameter_linestring('hrpt_201012011715_lvl0_smb.l0', 8, 'LINESTRING(-100 1, -101 11, -102 22, -103 33, -104 44)'::geography, '2010-12-01 16:10:00')
dcm.create_parameter_linestring('hrpt_201012011815_lvl0_smb.l0', 8, 'LINESTRING(12 55, 14 44, 16 37, 18 28, 20 9)'::geography, '2010-12-01 16:10:00')


