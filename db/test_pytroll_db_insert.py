#!/usr/bin/env python
#
#
#
# 
"""Insert test values into database through SQLAlchemy interface """

from datetime import datetime, timedelta
import shapely
import pytroll_db as db 
dcm = db.DCManager('postgresql://a001673:@localhost.localdomain:5432/sat_db')
dcm.create_parameter_type(1, 'dummy', 'parameter_value')


hrpt = dcm.create_file_type(1, 'HRPT', 'HRPT level 0 data')
hirlam = dcm.create_file_type(2, 'smhi_hirlam', 'HIRLAM data')
hrit = dcm.create_file_type(3, "HRIT", "met 9 hrit data")


hrpt_L0 = dcm.create_file_format(1, 'hrpt level 0', '')
grib = dcm.create_file_format(2, 'GRIB', '')


p_tofs = dcm.create_parameter(1, 1, 'time_of_first_scanline', '')
p_tols = dcm.create_parameter(2, 1, 'time_of_last_scanline', '')
p_on = dcm.create_parameter(3, 1, 'orbit_number', '')
p_satname = dcm.create_parameter(4, 1, 'satellite_name', '')
p_toa = dcm.create_parameter(5, 1, 'time_of_analysis', '')
p_fl = dcm.create_parameter(6, 1, 'forcast_length', '')
p_pc = dcm.create_parameter(7, 1, 'processing_center', '')
p_sst = dcm.create_parameter(8, 1, 'sub_satellite_track', '')

dcm.create_file_type_parameter(file_type=hrpt,
                               parameters=[p_tofs, p_tols, p_on,
                                           p_satname, p_sst])

dcm.create_file_type_parameter(file_type=hirlam,
                               parameters=[p_toa, p_fl, p_pc])

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

dcm.create_parameter_value(filename='hrpt_201012011615_lvl0_smb.l0',
                           parameter_name="time_of_first_scanline",
                           data_value=datetime(2010, 12, 1, 15, 55, 0),
                           creation_time=datetime(2010, 12, 1, 16, 15, 00))

dcm.create_parameter_value(filename='hrpt_201012011615_lvl0_smb.l0',
                           parameter_name="time_of_last_scanline",
                           data_value=datetime(2010, 12, 1, 16,10),
                           creation_time=datetime(2010, 12, 1, 16, 15))

dcm.create_parameter_value(filename='hrpt_201012011615_lvl0_smb.l0',
                           parameter_name="orbit_number",
                           data_value=2134,
                           creation_time=datetime(2010, 12, 1, 16, 15))

dcm.create_parameter_value(filename='hrpt_201012011615_lvl0_smb.l0',
                           parameter_name='satellite_name',
                           data_value='noaa19',
                           creation_time=datetime(2010, 12, 1, 16, 15))

dcm.create_parameter_value(filename='hirlam_2010_12_01_1200_areaB.grib',
                           parameter_name='time_of_analysis',
                           data_value=datetime(2010, 12, 1, 12, 0),
                           creation_time=datetime(2010, 12, 1, 16, 15))

dcm.create_parameter_value(filename='hirlam_2010_12_01_1200_areaB.grib',
                           parameter_name='forcast_length',
                           data_value=timedelta(hours=6),
                           creation_time=datetime(2010, 12, 1, 16, 15))

dcm.create_parameter_value(filename='hirlam_2010_12_01_1200_areaB.grib',
                           parameter_name='processing_center',
                           data_value=82,
                           creation_time=datetime(2010, 12, 1, 16, 15))

wkt_o = shapely.wkt.loads("LINESTRING(0 47.606, 3 51.5, 5 56, 10 59, 15 66)")
dcm.create_parameter_linestring(filename='hrpt_201012011615_lvl0_smb.l0',
                                parameter_name='sub_satellite_track',
                                linestring=wkt_o,
                                creation_time=datetime(2010, 12, 1, 16, 15))

wkt_o = shapely.wkt.loads("LINESTRING(-100 1, -101 11, -102 22, -103 33, -104 44)")
dcm.create_parameter_linestring(filename='hrpt_201012011715_lvl0_smb.l0',
                                parameter_name='sub_satellite_track',
                                linestring=wkt_o,
                                creation_time=datetime(2010, 12, 1, 16, 15))

wkt_o = shapely.wkt.loads("LINESTRING(12 55, 14 44, 16 37, 18 28, 20 9)")
dcm.create_parameter_linestring(filename='hrpt_201012011815_lvl0_smb.l0',
                                parameter_name='sub_satellite_track',
                                linestring=wkt_o,
                                creation_time=datetime(2010, 12, 1, 16, 15))
                           

dcm.create_file_uri(filename='hrpt_201012011615_lvl0_smb.l0',
                    URI="file:///data/24/saf/polar_in/rawdata/hrpt_201012011615_lvl0_smb.l0")

dcm.create_file_uri(filename='hrpt_201012011615_lvl0_smb.l0',
                    URI="file:///data/prodtest/saf/polar_in/rawdata/hrpt_201012011615_lvl0_smb.l0")

dcm.session.commit()


