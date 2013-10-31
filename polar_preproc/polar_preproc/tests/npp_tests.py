"""
Unit tests for NPP processing
"""

import unittest
import numpy
from tempfile import mkdtemp
import os

import polar_preproc.npp_granule as granule
import polar_preproc.segment as segment
import polar_preproc 

import datetime
import tempfile
    

HOME_DIR = os.path.dirname(__file__)

class TestNPPJsonIO(unittest.TestCase):
    """Testing reading a jason segment/granule file and writing it again"""
    
    def setUp(self):
        self.json_file = "%s/data/SDR_npp_d20120424_t1305467_e1307109_b02542_smb_dev.json" % HOME_DIR
        self.json_outfile = tempfile.mktemp()

    def test_read_write(self):
        """Test read and write a json message containing one NPP granule"""
        
        self.json_segment = segment.json_load(self.json_file)
        segment.json_dump(self.json_segment, self.json_outfile)
        segres = segment.json_load(self.json_outfile)
        
        self.assertTrue(str(segres) == str(self.json_segment))

    def tearDown(self):
        import os
        os.remove(self.json_outfile)


class TestNPPGranule(unittest.TestCase):
    """Testing the NPP Granule API"""
    def setUp(self):
        self.rdr_viirs = "RNSCA-RVIRS_npp_d20120514_t0505125_e0515086_b00001_c20120514051842618000_nfts_drl.h5"
        pass

    def test_get_granule_fields(self):
        """Test getting the granule fields from NPP VIIRS RDR and SDR files"""
        fields = granule.get_granule_fields(self.rdr_viirs, decode=False)

        self.assertTrue('kind' in fields)
        self.assertTrue('band' in fields)
        self.assertTrue('platform' in fields)
        self.assertTrue('date' in fields)
        self.assertTrue('start_time' in fields)
        self.assertTrue('end_time' in fields)
        self.assertTrue('orbit' in fields)
        self.assertTrue('create_time' in fields)
        self.assertTrue('site' in fields)

        #this = {'kind': 'RNSCA-RVIRS', 'platform': 'npp', 'start_time': '0505125', 'site': 'nfts', 
        #        'orbit': '00001', 'band': '', 'create_time': '20120514051842618000', 
        #        'end_time': '0515086', 'domain': 'drl', 'date': '20120514'}

        self.assertEqual(fields['kind'], 'RNSCA-RVIRS')
        self.assertEqual(fields['band'], '')
        self.assertEqual(fields['platform'], 'npp')
        self.assertEqual(fields['orbit'], '00001')
        self.assertEqual(fields['date'], '20120514')
        self.assertEqual(fields['start_time'], '0505125')
        self.assertEqual(fields['end_time'], '0515086')
        self.assertEqual(fields['create_time'], '20120514051842618000')
        self.assertEqual(fields['domain'], 'drl')

        fields = granule.get_granule_fields(self.rdr_viirs, decode=True)
        #print fields

        self.assertTrue('kind' in fields)
        self.assertTrue('band' in fields)
        self.assertTrue('platform' in fields)
        self.assertFalse('date' in fields)
        self.assertTrue('start_time' in fields)
        self.assertTrue('end_time' in fields)
        self.assertTrue('orbit' in fields)
        self.assertTrue('create_time' in fields)
        self.assertTrue('site' in fields)

        self.assertEqual(fields['kind'], 'RNSCA-RVIRS')
        self.assertEqual(fields['band'], '')
        self.assertEqual(fields['platform'], 'npp')
        self.assertEqual(fields['orbit'], 1)
        self.assertEqual(fields['start_time'], 
                         datetime.datetime(2012, 5, 14, 5, 5, 12, 500000))
        self.assertEqual(fields['end_time'], 
                         datetime.datetime(2012, 5, 14, 5, 15, 8, 600000))
        self.assertEqual(fields['create_time'], 
                         datetime.datetime(2012, 5, 14, 5, 18, 42, 618000))
        self.assertEqual(fields['domain'], 'drl')

    def test_npp_stamp(self):
        """Test getting a NPP stamp"""
        stamp = polar_preproc.get_npp_stamp(self.rdr_viirs)
        print stamp

    
        
    def tearDown(self):
        pass
        

if __name__ == "__main__":
    unittest.main()
