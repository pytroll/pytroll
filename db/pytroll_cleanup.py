import sys
import os
import glob
from datetime import datetime, timedelta

import pytroll_db

def delete_product(filename):
    dcm = pytroll_db.DCManager('postgresql://polar:polar@safe:5432/sat_db')
    
    file_obj = dcm.get_file(filename)
    dcm.delete(file_obj)
    dcm.save()

def sync_product_db(file_type_name, dirname, glob_filter):
    # Syncronize DB content with filesystem so no files exist in DB which are not present in filesystem
    filename_list = [os.path.basename(item) for item in glob.glob('%s/%s' % (dirname, glob_filter))]
    print 'filenames: ', filename_list
    dcm = pytroll_db.DCManager('postgresql://polar:polar@safe:5432/sat_db')
    file_type = dcm.get_file_type(file_type_name)
    file_obj_list = file_type.file_objs
    for file_obj in file_obj_list:
        if file_obj.filename not in filename_list:
            dcm.delete(file_obj)
    dcm.save()
 

def clean_old_entries_in_db(file_type_name, timestamp_utc):
    """Clean the DB for products of a given type with creation time older 
    than a given threshold"""

    dcm = pytroll_db.DCManager('postgresql://polar:polar@safe:5432/sat_db')
    file_list = dcm.get_files(file_type_name, newest_creation_time=timestamp_utc)
    for file_obj in file_list:
        dcm.delete(file_obj)
    dcm.save()

    
if __name__ == "__main__":
    clean_old_entries_in_db("PPS_cloud_type_granule", datetime(2011, 11, 11, 13, 25))
    #sync_product_db("PPS_cloud_type_granule", '/data/24/saf/polar_out/global', 'metop02*_cloudtype.h5')
    #sync_product_db("PPS_cloud_type_granule", '/tmp', 'metop02*_cloudtype.h5')
    #delete_product("metop02_20111110_1346_26252_satproj_00000_01079_cloudtype.h5")
