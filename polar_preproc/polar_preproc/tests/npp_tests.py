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
        self.rdr_filename = "RNSCA-RVIRS_npp_d20120514_t0505125_e0515086_b00001_c20120514051842618000_nfts_drl.h5"
        pass

    def test_get_granule_fields(self):
        """Test getting the granule fields from NPP VIIRS RDR and SDR files"""
        fields = granule.get_granule_fields(self.rdr_filename, decode=True)
    
        print fields
        self.assertTrue('kind' in fields)
        
    def tearDown(self):
        pass
        

if __name__ == "__main__":
    unittest.main()
