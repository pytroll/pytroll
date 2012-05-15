"""
Unit tests for NPP processing
"""

import unittest
import numpy
from tempfile import mkdtemp
import os

import polar_preproc.npp_granule as granule

class TestNPPGranule(unittest.TestCase):
    """Testung the NPP Granule API"""
    def setUp(self):
        self.rdr_viirs = "RNSCA-RVIRS_npp_d20120514_t0505125_e0515086_b00001_c20120514051842618000_nfts_drl.h5"
        pass

    def test_get_granule_fields(self):
        """Test getting the granule fields from NPP VIIRS RDR and SDR files"""
        fields = granule.get_granule_fields(self.rdr_viirs, decode=False)
        print fields

        self.assertTrue('kind' in fields)
        self.assertTrue('band' in fields)
        self.assertTrue('platform' in fields)
        self.assertTrue('date' in fields)
        self.assertTrue('start_time' in fields)
        self.assertTrue('end_time' in fields)
        self.assertTrue('orbit' in fields)
        self.assertTrue('create_time' in fields)
        self.assertTrue('site' in fields)

        self.assertEqual(fields['kind'], 'RNSCA-RVIRS')
        self.assertEqual(fields['band'], '')
        self.assertEqual(fields['platform'], 'npp')
        self.assertEqual(fields['date'], '20120514')
        self.assertEqual(fields['start_time'], '0505125')
        self.assertEqual(fields['end_time'], '0515086')

        fields = granule.get_granule_fields(self.rdr_viirs, decode=True)
        print fields


    def tearDown(self):
        pass
        

if __name__ == "__main__":
    unittest.main()
