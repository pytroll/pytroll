------------------------------
-- pgDesigner 1.2.17
--
-- Project    : pytroll_database
-- Date       : 12/08/2010 11:59:03.684
-- Description: Database layout for the pytroll project
-- DMI & SMHI
------------------------------


-- Start Table's declaration
DROP TABLE IF EXISTS "file_type" CASCADE;
CREATE TABLE "file_type" (
"file_type_id" int NOT NULL,
"file_type_name" character varying(50) NOT NULL,
"description" character varying(255) NOT NULL
) WITHOUT OIDS;
ALTER TABLE "file_type" ADD CONSTRAINT "file_type_id" PRIMARY KEY("file_type_id");

DROP TABLE IF EXISTS "file_format" CASCADE;
CREATE TABLE "file_format" (
"file_format_id" int NOT NULL,
"file_format_name" character varying(50) NOT NULL,
"description" character varying(255) NOT NULL
) WITHOUT OIDS;
ALTER TABLE "file_format" ADD CONSTRAINT "file_format_id" PRIMARY KEY("file_format_id");

DROP TABLE IF EXISTS "file" CASCADE;
CREATE TABLE "file" (
"filename" character varying(255) NOT NULL,
"file_type_id" int references file_type(file_type_id),
"file_format_id" int NOT NULL,
"is_archived" bool NOT NULL,
"created_time" timestamp NOT NULL
) WITH OIDS;
ALTER TABLE "file" ADD CONSTRAINT "filename" PRIMARY KEY("filename");

DROP TABLE IF EXISTS "parameter" CASCADE;
CREATE TABLE "parameter" (
"parameter_id" int NOT NULL,
"parameter_type_id" int,
"parameter_name" character varying(50) NOT NULL,
"description" character varying(255) NOT NULL
) WITH OIDS;
ALTER TABLE "parameter" ADD CONSTRAINT "parameter_id" PRIMARY KEY("parameter_id");

DROP TABLE IF EXISTS "parameter_type" CASCADE;
CREATE TABLE "parameter_type" (
"parameter_type_id" int NOT NULL,
"parameter_type_name" character varying(50) NOT NULL,
"parameter_location" character varying(50) CHECK ((parameter_location = 'parameter_value' or parameter_location = 'parameter_track'))
) WITH OIDS;
ALTER TABLE "parameter_type" ADD CONSTRAINT "parameter_type_id" PRIMARY KEY("parameter_type_id");

DROP TABLE IF EXISTS "parameter_value" CASCADE;
CREATE TABLE "parameter_value" (
"filename" character varying(255),
"parameter_id" int,
"creation_time" timestamp NOT NULL,
"data_value" character varying(3000) NOT NULL
) WITH OIDS;

DROP TABLE IF EXISTS "parameter_track" CASCADE;
CREATE TABLE "parameter_track" (
"filename" character varying(255),
"parameter_id" int,
"creation_time" timestamp NOT NULL,
"track" geography(linestring) NOT NULL
) WITH OIDS;

DROP TABLE IF EXISTS "boundary" CASCADE;
CREATE TABLE "boundary" (
"boundary_id" int NOT NULL,
"boundary_name" character varying(255) NOT NULL,
"creation_time" timestamp NOT NULL,
"boundary" geography(polygon) NOT NULL
) WITH OIDS;
ALTER TABLE "boundary" ADD CONSTRAINT "boundary_id" PRIMARY KEY("boundary_id");

DROP TABLE IF EXISTS "data_boundary" CASCADE;
CREATE TABLE "data_boundary" (
"filename" character varying(255),
"boundary_id" int,
"creation_time" timestamp NOT NULL
) WITH OIDS;

DROP TABLE IF EXISTS "tag" CASCADE;
CREATE TABLE "tag" (
"tag_id" int NOT NULL,
"tag" character varying(255) NOT NULL
) WITH OIDS;
ALTER TABLE "tag" ADD CONSTRAINT "tag_id" PRIMARY KEY("tag_id");

DROP TABLE IF EXISTS "file_type_tag" CASCADE;
CREATE TABLE "file_type_tag" (
"tag_id" int,
"file_type_id" int,
"creation_time" timestamp NOT NULL
) WITH OIDS;

DROP TABLE IF EXISTS "file_tag" CASCADE;
CREATE TABLE "file_tag" (
"tag_id" int,
"filename" character varying(255),
"creation_time" timestamp NOT NULL
) WITH OIDS;

DROP TABLE IF EXISTS "file_uri" CASCADE;
CREATE TABLE "file_uri" (
"file_type_id" int,
"file_format_id" int,
"uri" character varying(3000) NOT NULL
) WITH OIDS;

DROP TABLE IF EXISTS "file_type_parameter" CASCADE;
CREATE TABLE "file_type_parameter" (
"file_type_id" int,
"parameter_id" int
) WITH OIDS;

-- End Table's declaration

-- Start Relation's declaration
--ALTER TABLE "file" DROP CONSTRAINT "file_fkey1" CASCADE;
ALTER TABLE "file" ADD CONSTRAINT "file_fkey1" FOREIGN KEY ("file_type_id") REFERENCES "file_type"("file_type_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "file" DROP CONSTRAINT "file_fkey2" CASCADE;
ALTER TABLE "file" ADD CONSTRAINT "file_fkey2" FOREIGN KEY ("file_format_id") REFERENCES "file_format"("file_format_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "parameter" DROP CONSTRAINT "parameter_fkey1" CASCADE;
ALTER TABLE "parameter" ADD CONSTRAINT "parameter_fkey1" FOREIGN KEY ("parameter_type_id") REFERENCES "parameter_type"("parameter_type_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "parameter_value" DROP CONSTRAINT "parameter_value_fkey1" CASCADE;
ALTER TABLE "parameter_value" ADD CONSTRAINT "parameter_value_fkey1" FOREIGN KEY ("parameter_id") REFERENCES "parameter"("parameter_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "parameter_value" DROP CONSTRAINT "parameter_value_fkey2" CASCADE;
ALTER TABLE "parameter_value" ADD CONSTRAINT "parameter_value_fkey2" FOREIGN KEY ("filename") REFERENCES "file"("filename") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "parameter_track" DROP CONSTRAINT "parameter_track_fkey1" CASCADE;
ALTER TABLE "parameter_track" ADD CONSTRAINT "parameter_track_fkey1" FOREIGN KEY ("filename") REFERENCES "file"("filename") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "parameter_track" DROP CONSTRAINT "parameter_track_fkey2" CASCADE;
ALTER TABLE "parameter_track" ADD CONSTRAINT "parameter_track_fkey2" FOREIGN KEY ("parameter_id") REFERENCES "parameter"("parameter_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "data_boundary" DROP CONSTRAINT "data_boundary_fkey1" CASCADE;
ALTER TABLE "data_boundary" ADD CONSTRAINT "data_boundary_fkey1" FOREIGN KEY ("boundary_id") REFERENCES "boundary"("boundary_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "file_type_tag" DROP CONSTRAINT "file_type_tag_fkey1" CASCADE;
ALTER TABLE "file_type_tag" ADD CONSTRAINT "file_type_tag_fkey1" FOREIGN KEY ("tag_id") REFERENCES "tag"("tag_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "file_tag" DROP CONSTRAINT "file_tag_fkey1" CASCADE;
ALTER TABLE "file_tag" ADD CONSTRAINT "file_tag_fkey1" FOREIGN KEY ("tag_id") REFERENCES "tag"("tag_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "file_uri" DROP CONSTRAINT "file_uri_fkey1" CASCADE;
ALTER TABLE "file_uri" ADD CONSTRAINT "file_uri_fkey1" FOREIGN KEY ("file_format_id") REFERENCES "file_format"("file_format_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "file_uri" DROP CONSTRAINT "file_uri_fkey2" CASCADE;
ALTER TABLE "file_uri" ADD CONSTRAINT "file_uri_fkey2" FOREIGN KEY ("file_type_id") REFERENCES "file_type"("file_type_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "file_type_parameter" DROP CONSTRAINT "file_type_parameter_fkey1" CASCADE;
ALTER TABLE "file_type_parameter" ADD CONSTRAINT "file_type_parameter_fkey1" FOREIGN KEY ("parameter_id") REFERENCES "parameter"("parameter_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "file_type_parameter" DROP CONSTRAINT "file_type_parameter_fkey2" CASCADE;
ALTER TABLE "file_type_parameter" ADD CONSTRAINT "file_type_parameter_fkey2" FOREIGN KEY ("file_type_id") REFERENCES "file_type"("file_type_id") ON UPDATE RESTRICT ON DELETE RESTRICT;

--ALTER TABLE "data_boundary" DROP CONSTRAINT "data_boundary_fkey2" CASCADE;
ALTER TABLE "data_boundary" ADD CONSTRAINT "data_boundary_fkey2" FOREIGN KEY ("filename") REFERENCES "file"("filename") ON UPDATE RESTRICT ON DELETE RESTRICT;

-- End Relation's declaration

