
insert into file_type values(1, 'PPS_cloud_type_granule', 'NWCSAF PPS cloud type on swath granule');

insert into file_format values(1, 'HDF5', 'Hierarchical Data Format version 5');

insert into parameter_type values(1, 'datetime', 'parameter_value');
insert into parameter_type values(2, 'int', 'parameter_value');
insert into parameter_type values(3, 'str', 'parameter_value');
insert into parameter_type values(4, 'linestring', 'parameter_linestring');

insert into parameter values(1, 1, 'time_start', 'Start time of observation');
insert into parameter values(2, 1, 'time_end', 'End time of observation');
insert into parameter values(3, 2, 'orbit_number', 'Orbit number');
insert into parameter values(4, 3, 'satellite_name', 'Name of satellite');
insert into parameter values(5, 4, 'sub_satellite_track', 'Sub satellite track');

insert into file_type_parameter values(1, 1);
insert into file_type_parameter values(1, 2);
insert into file_type_parameter values(1, 3);
insert into file_type_parameter values(1, 4);
insert into file_type_parameter values(1, 5);

insert into file_access_uri values(1, 1, 1, 'file:///data/24/saf/polar_out/global');

