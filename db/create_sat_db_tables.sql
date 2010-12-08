create table file_type(
file_type_id int primary key,
file_type_name varchar(50) not null,
description varchar(255) not null
);

create table file_format(
file_format_id int primary key,
file_format_name varchar(50) not null,
description varchar(255) not null
);

create table file(
filename varchar(255) primary key,
file_type_id int references file_type(file_type_id),
file_format_id int references file_format(file_format_id),
is_arcived bool not null,
created_time timestamp not null
);

create table parameter_type(
parameter_type_id int primary key,
parameter_type_name varchar(50) not null,
parameter_location varchar(50) check (parameter_location = 'parameter_value' or parameter_location = 'parameter_track')
);

create table parameter(
parameter_id int primary key,
parameter_type_id int references parameter_type(parameter_type_id),
parameter_name varchar(50) not null,
description varchar(255) not null
);

create table file_type_parameter(
file_type_id int references file_type(file_type_id),
parameter_id int references parameter(parameter_id),
primary key (file_type_id, parameter_id)
);

create table parameter_value(
filename varchar(255) references file(filename),
parameter_id int references parameter(parameter_id),
created_time timestamp not null,
data_value varchar(3000) not null
);

create table parameter_track(
filename varchar(255) references file(filename),
parameter_id int references parameter(parameter_id),
created_time timestamp not null,
track geography(linestring) not null
);

create table boundary(
boundary_id int primary key,
boundary_name varchar(255) not null,
created_time timestamp not null,
boundary geography(polygon) not null
);

create table data_boundary(
filename varchar(255) references file(filename),
boundary_id int references boundary(boundary_id),
created_time timestamp not null,
primary key (filename, boundary_id)
);

create table tag(
tag_id int primary key,
tag varchar(255) not null
);

create table file_type_tag(
tag_id int references tag(tag_id),
file_type_id int references file_type(file_type_id),
created_time timestamp not null
);

create table file_tag(
tag_id int references tag(tag_id),
filename varchar(255) references file(filename),
created_time timestamp not null
);

create table file_URI(
file_type_id int references file_type(file_type_id),
file_format_id int references file_format(file_format_id),
URI varchar(3000) not null
);
