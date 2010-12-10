#!/usr/bin/env python

import sys


def usage():
    print """postgisify_pytroll_db.py infile.sql outfil.sql"""
    print """where - """
    print """infile.sql - Power Arcitect generated pytroll_db SQL"""
    print """outfile.sql - pytroll_db SQL with correct PostGIS types"""
    exit(1)

args = sys.argv[1:]

if len(args) != 2:
    usage()

postgis_sql = ''
infile = open(args[0])
for line in infile:
    if 'track' in line:
        line = line.replace('OTHER', 'geography(linestring)')
    elif 'boundary' in line:
        line = line.replace('OTHER', 'geography(polygon)')
    postgis_sql += line

postgis_sql += '\n'
postgis_sql += 'CREATE INDEX track_gix ON parameter_track USING GIST (track);\n'
postgis_sql += 'CREATE INDEX boundary_gix ON boundary USING GIST (boundary);\n'


infile.close()
open(args[1], 'w').write(postgis_sql)
    
    
