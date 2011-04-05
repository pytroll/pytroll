

CREATE TABLE public.boundary (
                boundary_id INTEGER NOT NULL,
                boundary_name VARCHAR(255) NOT NULL,
                boundary geography(polygon) NOT NULL,
                creation_time INTEGER NOT NULL,
                CONSTRAINT boundary_pk PRIMARY KEY (boundary_id)
);


CREATE TABLE public.parameter_type (
                parameter_type_id INTEGER NOT NULL,
                parameter_type_name VARCHAR(50) NOT NULL,
                parameter_location VARCHAR(50) NOT NULL,
                CONSTRAINT parameter_type_pk PRIMARY KEY (parameter_type_id)
);


CREATE TABLE public.parameter (
                parameter_id INTEGER NOT NULL,
                parameter_type_id INTEGER NOT NULL,
                parameter_name VARCHAR(50) NOT NULL,
                description VARCHAR(255) NOT NULL,
                CONSTRAINT parameter_pk PRIMARY KEY (parameter_id)
);


CREATE TABLE public.tag (
                tag_id INTEGER NOT NULL,
                tag VARCHAR(255) NOT NULL,
                CONSTRAINT tag_pk PRIMARY KEY (tag_id)
);


CREATE TABLE public.file_format (
                file_format_id INTEGER NOT NULL,
                file_format_name VARCHAR(50) NOT NULL,
                description VARCHAR(255) NOT NULL,
                CONSTRAINT file_format_pk PRIMARY KEY (file_format_id)
);


CREATE TABLE public.file_type (
                file_type_id INTEGER NOT NULL,
                file_type_name VARCHAR(50) NOT NULL,
                description VARCHAR(255) NOT NULL,
                CONSTRAINT file_type_pk PRIMARY KEY (file_type_id)
);


CREATE TABLE public.file_type_parameter (
                file_type_id INTEGER NOT NULL,
                parameter_id INTEGER NOT NULL,
                CONSTRAINT file_type_parameter_pk PRIMARY KEY (file_type_id, parameter_id)
);


CREATE TABLE public.file (
                filename VARCHAR(255) NOT NULL,
                file_type_id INTEGER NOT NULL,
                file_format_id INTEGER NOT NULL,
                is_archived BOOLEAN NOT NULL,
                creation_time TIMESTAMP NOT NULL,
                CONSTRAINT file_pk PRIMARY KEY (filename)
);


CREATE INDEX file_idx
 ON public.file
 ( file_type_id, file_format_id );

CREATE TABLE public.data_boundary (
                filename VARCHAR(255) NOT NULL,
                boundary_id INTEGER NOT NULL,
                creation_time TIMESTAMP NOT NULL,
                CONSTRAINT data_boundary_pk PRIMARY KEY (filename, boundary_id)
);


CREATE TABLE public.parameter_linestring (
                filename VARCHAR(255) NOT NULL,
                parameter_id INTEGER NOT NULL,
                data_value geography(linestring) NOT NULL,
                creation_time TIMESTAMP NOT NULL,
                CONSTRAINT parameter_linestring_pk PRIMARY KEY (filename, parameter_id)
);


CREATE TABLE public.parameter_value (
                filename VARCHAR(255) NOT NULL,
                parameter_id INTEGER NOT NULL,
                data_value VARCHAR(3000) NOT NULL,
                creation_time TIMESTAMP NOT NULL,
                CONSTRAINT parameter_value_pk PRIMARY KEY (filename, parameter_id)
);


CREATE TABLE public.file_tag (
                tag_id INTEGER NOT NULL,
                filename VARCHAR(255) NOT NULL,
                creation_time TIMESTAMP NOT NULL,
                CONSTRAINT file_tag_pk PRIMARY KEY (tag_id, filename)
);


CREATE TABLE public.file_uri (
                file_type_id INTEGER NOT NULL,
                file_format_id INTEGER NOT NULL,
                sequence INTEGER DEFAULT 1 NOT NULL,
                uri VARCHAR(3000) NOT NULL,
                CONSTRAINT file_uri_pk PRIMARY KEY (file_type_id, file_format_id, sequence)
);


CREATE TABLE public.file_type_tag (
                tag_id INTEGER NOT NULL,
                file_type_id INTEGER NOT NULL,
                creation_time TIMESTAMP NOT NULL,
                CONSTRAINT file_type_tag_pk PRIMARY KEY (tag_id, file_type_id)
);


ALTER TABLE public.data_boundary ADD CONSTRAINT boundary_data_boundary_fk
FOREIGN KEY (boundary_id)
REFERENCES public.boundary (boundary_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.parameter ADD CONSTRAINT parameter_type_parameter_fk
FOREIGN KEY (parameter_type_id)
REFERENCES public.parameter_type (parameter_type_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.parameter_value ADD CONSTRAINT parameter_parameter_value_fk
FOREIGN KEY (parameter_id)
REFERENCES public.parameter (parameter_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.parameter_linestring ADD CONSTRAINT parameter_parameter_track_fk
FOREIGN KEY (parameter_id)
REFERENCES public.parameter (parameter_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.file_type_parameter ADD CONSTRAINT parameter_file_type_parameter_fk
FOREIGN KEY (parameter_id)
REFERENCES public.parameter (parameter_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.file_type_tag ADD CONSTRAINT tag_file_type_tag_fk
FOREIGN KEY (tag_id)
REFERENCES public.tag (tag_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.file_tag ADD CONSTRAINT tag_file_tag_fk
FOREIGN KEY (tag_id)
REFERENCES public.tag (tag_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.file_uri ADD CONSTRAINT file_format_file_uri_fk
FOREIGN KEY (file_format_id)
REFERENCES public.file_format (file_format_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.file ADD CONSTRAINT file_format_file_fk
FOREIGN KEY (file_format_id)
REFERENCES public.file_format (file_format_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.file_type_tag ADD CONSTRAINT file_type_file_type_tag_fk
FOREIGN KEY (file_type_id)
REFERENCES public.file_type (file_type_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.file_uri ADD CONSTRAINT file_type_file_uri_fk
FOREIGN KEY (file_type_id)
REFERENCES public.file_type (file_type_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.file ADD CONSTRAINT file_type_file_fk
FOREIGN KEY (file_type_id)
REFERENCES public.file_type (file_type_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.file_type_parameter ADD CONSTRAINT file_type_file_type_parameter_fk
FOREIGN KEY (file_type_id)
REFERENCES public.file_type (file_type_id)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.file_tag ADD CONSTRAINT file_file_tag_fk
FOREIGN KEY (filename)
REFERENCES public.file (filename)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.parameter_value ADD CONSTRAINT file_parameter_value_fk
FOREIGN KEY (filename)
REFERENCES public.file (filename)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.parameter_linestring ADD CONSTRAINT file_parameter_track_fk
FOREIGN KEY (filename)
REFERENCES public.file (filename)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;

ALTER TABLE public.data_boundary ADD CONSTRAINT file_data_boundary_fk
FOREIGN KEY (filename)
REFERENCES public.file (filename)
ON DELETE NO ACTION
ON UPDATE NO ACTION
NOT DEFERRABLE;


CREATE INDEX track_gix ON parameter_linestring USING GIST (data_value);
CREATE INDEX boundary_gix ON boundary USING GIST (boundary);

