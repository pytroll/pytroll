import sys
import os
import glob
from datetime import datetime, timedelta

import pytroll_db

DB = "postgresql://safusr.u:NWCsaf22@postgresutv01/sat_db"

def delete_product(filename):
    dcm = pytroll_db.DCManager(DB)
    
    file_obj = dcm.get_file(filename)
    dcm.delete(file_obj)
    dcm.save()

def sync_product_db(file_type_name, dirname, glob_filter):
    # Syncronize DB content with filesystem so no files exist in DB which are not present in filesystem
    filename_list = [os.path.basename(item) for item in glob.glob('%s/%s' % (dirname, glob_filter))]
    print 'filenames: ', filename_list
    dcm = pytroll_db.DCManager(DB)
    file_type = dcm.get_file_type(file_type_name)
    file_obj_list = file_type.file_objs
    for file_obj in file_obj_list:
        if file_obj.filename not in filename_list:
            dcm.delete(file_obj)
    dcm.save()
 

def clean_old_entries_in_db(file_type_name, timestamp_utc):
    """Clean the DB for products of a given type with creation time older 
    than a given threshold"""

    dcm = pytroll_db.DCManager(DB)
    file_list = dcm.get_files(file_type_name, newest_creation_time=timestamp_utc)
    for file_obj in file_list:
        dcm.delete(file_obj)
    dcm.save()


import paramiko
from urlparse import urlparse
from socket import gaierror

logins = {}

import ConfigParser

def load_logins():
    cfg = ConfigParser.ConfigParser()
    cfg.read("access.cfg")

    global logins

    for host in cfg.sections():
        logins[host] = (cfg.get(host, "username"),
                        cfg.get(host, "password"))
    

class ConnectionError(Exception):
    pass

def check_file_ssh(uri):
    parsed = urlparse(uri)
    if parsed.scheme != "ssh":
        raise ValueError("Protocol should be ssh, not " + str(parsed.scheme))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    username, password = logins.get(parsed.hostname,
                                    (parsed.hostname, parsed.password))
    try:
        ssh.connect(parsed.hostname,
                    username=username,
                    password=password)
    except gaierror:
        raise ConnectionError("Can't access " + parsed.hostname
                              + " as " + str(username))
    except paramiko.PasswordRequiredException:
        raise ConnectionError("Password required for user "
                              + str(username) + " on "
                              + str(parsed.hostname))
    ftp = ssh.open_sftp()
    
    try:
        ftp.stat(parsed.path)
    except IOError:
        return False
    else:
        return True

connexions = {}

def cached_check_file_ssh(uri):
    global connexions
    parsed = urlparse(uri)
    if parsed.scheme != "ssh":
        raise ValueError("Protocol should be ssh, not " + str(parsed.scheme))

    if parsed.hostname in connexions:
        ftp = connexions[parsed.hostname]
    else:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        username, password = logins.get(parsed.hostname,
                                        (parsed.hostname, parsed.password))
        try:
            ssh.connect(parsed.hostname,
                        username=username,
                        password=password)
        except gaierror:
            raise ConnectionError("Can't access " + parsed.hostname
                                  + " as " + str(username))
        except paramiko.PasswordRequiredException:
            raise ConnectionError("Password required for user "
                                  + str(username) + " on "
                                  + str(parsed.hostname))
        ftp = ssh.open_sftp()
        connexions[parsed.hostname] = ftp
    try:
        ftp.stat(parsed.path)
    except IOError:
        return False
    else:
        return True

def close_ssh_all():
    global connexion
    del connexion


from threading import Thread, Condition
from Queue import Queue, Empty
class SSHChecker(Thread):
    """Check if a file is there via SSH.
    """

    def __init__(self, hostname, queue, returnqueue):
        Thread.__init__(self)
        self.queue = queue
        self.returnqueue = returnqueue
        self.loop = True
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            username, password = logins[hostname]
        except KeyError:
            print "unknown hostname", hostname
            raise
        try:
            self.ssh.connect(hostname,
                             username=username,
                             password=password)
        except gaierror:
            raise ConnectionError("Can't access " + hostname
                                  + " as " + str(username))
        except paramiko.PasswordRequiredException:
            raise ConnectionError("Password required for user "
                                  + str(username) + " on "
                                  + str(hostname))
        self.ftp = self.ssh.open_sftp()

    def run(self):
        while self.loop:
            try:
                uri = self.queue.get(timeout=1)
            except Empty:
                continue
            try:
                parsed = urlparse(uri)
                self.ftp.stat(parsed.path)
            except IOError:
                self.returnqueue.put((uri, False))
            else:
                self.returnqueue.put((uri, True))
                
    def stop(self):
        self.loop = False

connexions = {}
returnqueue = Queue()

def check_file_threaded(uri):
    global connexions
    parsed = urlparse(uri)
    if parsed.scheme == "file":
        print "skipping", uri
        return
    if parsed.scheme != "ssh":
        raise ValueError("Protocol should be ssh, not " + str(parsed.scheme))
    if parsed.hostname not in connexions:
        connexions[parsed.hostname] = SSHChecker(parsed.hostname,
                                                 Queue(),
                                                 returnqueue)
        connexions[parsed.hostname].start()
    connexions[parsed.hostname].queue.put(uri)
        

def is_there_dict(file_list):
    cnt = 0
    for filename in file_list:
        for uri in filename.uris:
            cnt += 1
            check_file_threaded(uri.uri)
    print "send", cnt, "requests..."
    values = {}
    while True:
        try:
            res = returnqueue.get(timeout=2)
        except Empty:
            for connexion in connexions:
                connexions[connexion].stop()
            return values
        values[res[0]] = res[1]
        
def threaded_check_all():
    dcm = pytroll_db.DCManager(DB)
    file_list = dcm.get_files()

    load_logins()
    print "requesting..."
    result = is_there_dict(file_list)
    cnt = 0
    removed = 0
    print "checking..."
    for filename in file_list:
        uris_remove = []
        for uri in filename.uris:
            cnt += 1
            is_there = result[uri.uri]
            if not is_there:
                removed += 1
                uris_remove.append(uri)
        if len(uris_remove) == len(filename.uris):
            dcm.delete(filename)
        for uri in uris_remove:
            dcm.delete(uri)
    dcm.save()
    print "Removed", removed, "out of", cnt

def check_all():
    dcm = pytroll_db.DCManager(DB)
    file_list = dcm.get_files()

    load_logins()

    for filename in file_list:
        uris_remove = []
        for uri in filename.uris:
            try:
                is_there = cached_check_file_ssh(uri.uri)
            except ConnectionError:
                print "Can't connect, skipping", uri.uri
                continue
            if not is_there:
                print "Missing:", uri.uri
                uris_remove.append(uri)
            else:
                print "Present:", uri.uri

        if len(uris_remove) == len(filename.uris):
            print "removing", filename
            dcm.delete(filename)
        for uri in uris_remove:
            print "removing", uri
            dcm.delete(uri)
    dcm.save()
if __name__ == "__main__":
    #clean_old_entries_in_db("PPS_cloud_type_granule", datetime(2011, 11, 11, 13, 25))
    #sync_product_db("PPS_cloud_type_granule", '/data/24/saf/polar_out/global', 'metop02*_cloudtype.h5')
    #sync_product_db("PPS_cloud_type_granule", '/tmp', 'metop02*_cloudtype.h5')
    #delete_product("metop02_20111110_1346_26252_satproj_00000_01079_cloudtype.h5")
    threaded_check_all()
