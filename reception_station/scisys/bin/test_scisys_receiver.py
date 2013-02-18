#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Test suite for the scisys receiver.
"""



# Test cases.

import unittest

input_stoprc = '<message timestamp="2013-02-18T09:21:35" sequence="7482" severity="INFO" messageID="0" type="2met.message" sourcePU="SMHI-Linux" sourceSU="POESAcquisition" sourceModule="POES" sourceInstance="1"><body>STOPRC Stop reception: Satellite: NPP, Orbit number: 6796, Risetime: 2013-02-18 09:08:09, Falltime: 2013-02-18 09:21:33</body></message>'

input_dispatch_viirs = '<message timestamp="2013-02-18T09:24:20" sequence="27098" severity="INFO" messageID="8250" type="2met.filehandler.sink.success" sourcePU="SMHI-Linux" sourceSU="GMCSERVER" sourceModule="GMCSERVER" sourceInstance="1"><body>FILDIS File Dispatch: /data/npp/RNSCA-RVIRS_npp_d20130218_t0908103_e0921256_b00001_c20130218092411165000_nfts_drl.h5 /archive/npp/RNSCA-RVIRS_npp_d20130218_t0908103_e0921256_b00001_c20130218092411165000_nfts_drl.h5</body></message>'

input_dispatch_atms = '<message timestamp="2013-02-18T09:24:21" sequence="27100" severity="INFO" messageID="8250" type="2met.filehandler.sink.success" sourcePU="SMHI-Linux" sourceSU="GMCSERVER" sourceModule="GMCSERVER" sourceInstance="1"><body>FILDIS File Dispatch: /data/npp/RATMS-RNSCA_npp_d20130218_t0908194_e0921055_b00001_c20130218092411244000_nfts_drl.h5 /archive/npp/RATMS-RNSCA_npp_d20130218_t0908194_e0921055_b00001_c20130218092411244000_nfts_drl.h5</body></message>'

from scisys_receiver import TwoMetMessage, MessageReceiver
import datetime

viirs = {'satellite': 'NPP', 'format': 'RDR', 'start_time': datetime.datetime(2013, 2, 18, 9, 8, 9), 'level': '0', 'orbit_number': 6796, 'uri': 'ssh://bla/archive/npp/RNSCA-RVIRS_npp_d20130218_t0908103_e0921256_b00001_c20130218092411165000_nfts_drl.h5', 'filename': 'RNSCA-RVIRS_npp_d20130218_t0908103_e0921256_b00001_c20130218092411165000_nfts_drl.h5', 'instrument': 'viirs', 'end_time': datetime.datetime(2013, 2, 18, 9, 21, 33), 'type': 'HDF5'}

atms = {'satellite': 'NPP', 'format': 'RDR', 'start_time': datetime.datetime(2013, 2, 18, 9, 8, 9), 'level': '0', 'orbit_number': 6796, 'uri': 'ssh://bla/archive/npp/RATMS-RNSCA_npp_d20130218_t0908194_e0921055_b00001_c20130218092411244000_nfts_drl.h5', 'filename': 'RATMS-RNSCA_npp_d20130218_t0908194_e0921055_b00001_c20130218092411244000_nfts_drl.h5', 'instrument': 'atms', 'end_time': datetime.datetime(2013, 2, 18, 9, 21, 33), 'type': 'HDF5'}


class ScisysReceiverTest(unittest.TestCase):

    def test_reception(self):
        msg_rec = MessageReceiver("bla")

        string = TwoMetMessage(input_stoprc)

        to_send = msg_rec.receive(string)

        self.assertTrue(to_send is None)

        string = TwoMetMessage(input_dispatch_viirs)

        to_send = msg_rec.receive(string)

        self.assertTrue(to_send == viirs)

        string = TwoMetMessage(input_dispatch_atms)

        to_send = msg_rec.receive(string)

        self.assertTrue(to_send == atms)

        

if __name__ == '__main__':
    unittest.main()
