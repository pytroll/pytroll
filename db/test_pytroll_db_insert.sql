
insert into file_type values(1, 'HRPT', 'HRPT level 0 data');
insert into file_type values(2, 'smhi_hirlam', 'HIRLAM data');

insert into file_format values(1, 'hrpt level 0', '');
insert into file_format values(2, 'GRIB', '');

insert into parameter_type values(1, 'dummy', 'parameter_value');

insert into parameter values(1, 1, 'time_of_first_scanline', '');
insert into parameter values(2, 1, 'time_of_last_scanline', '');
insert into parameter values(3, 1, 'orbit_number', '');
insert into parameter values(4, 1, 'satellite_name', '');
insert into parameter values(5, 1, 'time_of_analysis', '');
insert into parameter values(6, 1, 'forcast_length', '');
insert into parameter values(7, 1, 'processing_center', '');
insert into parameter values(8, 1, 'sub_satellite_track', '');

insert into file_type_parameter values(1, 1);
insert into file_type_parameter values(1, 2);
insert into file_type_parameter values(1, 3);
insert into file_type_parameter values(1, 4);
insert into file_type_parameter values(1, 8);
insert into file_type_parameter values(2, 5);
insert into file_type_parameter values(2, 6);
insert into file_type_parameter values(2, 7);

insert into file values('hrpt_201012011615_lvl0_smb.l0', 1, 1, false, timestamp '2010-12-01 16:15:00');
insert into file values('hirlam_2010_12_01_1200_areaB.grib', 2, 2, false, timestamp '2010-12-01 12:07:00');
insert into file values('hrpt_201012011715_lvl0_smb.l0', 1, 1, false, '2010-12-01 17:10:00');
insert into file values('hrpt_201012011815_lvl0_smb.l0', 1, 1, false, '2010-12-01 18:10:00');

insert into parameter_value values('hrpt_201012011615_lvl0_smb.l0', 1, '2010-12-01 15:55:00', '2010-12-01 16:15:00');

insert into parameter_value values('hrpt_201012011615_lvl0_smb.l0', 2, '2010-12-01 16:10:00', '2010-12-01 16:15:00');
insert into parameter_value values('hrpt_201012011615_lvl0_smb.l0', 3, '2134', '2010-12-01 16:15:00');
insert into parameter_value values('hrpt_201012011615_lvl0_smb.l0', 4, '19', '2010-12-01 16:15:00');
insert into parameter_value values('hirlam_2010_12_01_1200_areaB.grib', 5, '2010-12-01 12:00:00', '2010-12-01 16:15:00');
insert into parameter_value values('hirlam_2010_12_01_1200_areaB.grib', 6, '6', '2010-12-01 16:15:00');
insert into parameter_value values('hirlam_2010_12_01_1200_areaB.grib', 7, '82', '2010-12-01 16:15:00');

insert into parameter_linestring values('hrpt_201012011615_lvl0_smb.l0', 8, 'LINESTRING(0 47.606, 3 51.5, 5 56, 10 59, 15 66)'::geography, '2010-12-01 16:10:00');
insert into parameter_linestring values('hrpt_201012011715_lvl0_smb.l0', 8, 'LINESTRING(-100 1, -101 11, -102 22, -103 33, -104 44)'::geography, '2010-12-01 16:10:00');
insert into parameter_linestring values('hrpt_201012011815_lvl0_smb.l0', 8, 'LINESTRING(12 55, 14 44, 16 37, 18 28, 20 9)'::geography, '2010-12-01 16:10:00');

