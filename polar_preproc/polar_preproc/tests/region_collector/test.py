

import datetime
import json


#start_time = datetime.datetime(2012,5,15,11,21)
start_time = datetime.datetime(2012,5,15,11,5)
dt = datetime.timedelta(seconds=85.5)

npp_json_template = [{
        "create_time": "2012-05-03T15:00:50.939948", 
        "description": "A SDR Granule", 
        "domain": "dev", 
        "end_time": "2012-04-24T13:07:10.900000", 
        "orbit_number": 2542, 
        "platform": "npp", 
        "site": "smb", 
        "start_time": "2012-04-24T13:05:46.700000"}]



for step in range(30):
    granule_start_time = start_time + step * dt
    npp_json_template[0]['start_time'] = granule_start_time.isoformat()
    granule_end_time = start_time + (step + 1) * dt
    npp_json_template[0]['end_time'] = granule_end_time.isoformat()
    with open("npp_%s.json" % granule_start_time.strftime("%Y%m%d%H%M"), 'w' ) as jfp:
        json.dump(npp_json_template, jfp, sort_keys=True, indent=4)


