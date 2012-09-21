#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012 Martin Raspaud

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

"""
"""

TEST_DATA_NPP = """Message[ID='0', type='2met.message', time='05 07 2012 - 07:16:24', body='STOPRC Stop reception: Satellite: NPP, Orbit number: 3560, Risetime: 2012-07-05 07:06:48, Falltime: 2012-07-05 07:16:24']
Message[ID='8250', type='2met.filehandler.sink.success', time='05 07 2012 - 07:19:57', body='FILDIS File Dispatch: /data/npp/RNSCA-RVIRS_npp_d20120705_t0706492_e0716204_b00001_c20120705071952092000_nfts_drl.h5 /archive/npp/RNSCA-RVIRS_npp_d20120705_t0706492_e0716204_b00001_c20120705071952092000_nfts_drl.h5']
Message[ID='8250', type='2met.filehandler.sink.success', time='05 07 2012 - 07:19:58', body='FILDIS File Dispatch: /data/npp/RCRIS-RNSCA_npp_d20120705_t0706508_e0716230_b00001_c20120705071952132000_nfts_drl.h5 /archive/npp/RCRIS-RNSCA_npp_d20120705_t0706508_e0716230_b00001_c20120705071952132000_nfts_drl.h5']
Message[ID='8250', type='2met.filehandler.sink.success', time='05 07 2012 - 07:19:58', body='FILDIS File Dispatch: /data/npp/RATMS-RNSCA_npp_d20120705_t0706500_e0715388_b00001_c20120705071952147000_nfts_drl.h5 /archive/npp/RATMS-RNSCA_npp_d20120705_t0706500_e0715388_b00001_c20120705071952147000_nfts_drl.h5']"""
TEST_DATA_NOAA19 = """Message[ID='0', type='2met.message', time='12 01 2012 - 11:35:20', body='STOPRC Stop reception: Satellite: NOAA 19, Orbit number: 15090, Risetime: 2012-01-12 11:19:32, Falltime: 2012-01-12 11:35:20']
Message[ID='0', type='2met.message', time='12 01 2012 - 11:35:20', body='STOPRC HRPTFrameSync stops reception. Rename raw data file to /data/hrpt/20120112111932_NOAA_19.hmf']
Message[ID='0', type='2met.message', time='12 01 2012 - 11:35:20', body='STOPRC HRPTFrameSync closed analyze file']
Message[ID='8250', type='2met.filehandler.sink.success', time='12 01 2012 - 11:35:23', body='FILDIS File Dispatch: /data/hrpt/20120112111932_NOAA_19.hmf /archive/hrpt/20120112111932_NOAA_19.hmf']
Message[ID='8250', type='2met.filehandler.sink.success', time='12 01 2012 - 11:35:25', body='FILDIS File Dispatch: /data/hrpt/20120112111932_NOAA_19.hmf ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/hrpt']
Message[ID='8250', type='2met.filehandler.sink.success', time='12 01 2012 - 11:35:26', body='FILDIS File Dispatch: /data/hrpt/20120112111932_NOAA_19.hmf ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/hrpt']"""

TEST_DATA_TERRA = """Message[ID='0', type='2met.message', time='23 01 2012 - 22:10:25', body='STOPRC Stop reception: Satellite: TERRA, Orbit number: 64360, Risetime: 2012-01-23 21:57:43, Falltime: 2012-01-23 22:10:25']
Message[ID='0', type='2met.message', time='23 01 2012 - 22:10:25', body='STOPRC Send HW Controller the stopReception command']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:00', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743001.PDS /archive/modis/P0420064AAAAAAAAAAAAAA12023215743001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:00', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743000.PDS /archive/modis/P0420064AAAAAAAAAAAAAA12023215743000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:02', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:03', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:03', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:03', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:04', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='23 01 2012 - 22:12:04', body='FILDIS File Dispatch: /data/modis/P0420064AAAAAAAAAAAAAA12023215743000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']"""
TEST_DATA_AQUA = """Message[ID='0', type='2met.message', time='24 01 2012 - 00:35:21', body='STOPRC Stop reception: Satellite: AQUA, Orbit number: 51722, Risetime: 2012-01-24 00:21:39, Falltime: 2012-01-24 00:35:21']
Message[ID='0', type='2met.message', time='24 01 2012 - 00:35:21', body='STOPRC Send HW Controller the stopReception command']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540342AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540064AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540220AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540290AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540141AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540114AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540290AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540261AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540157AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540404AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540407AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540414AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540415AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540414AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540404AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540266AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540406AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540220AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540064AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540262AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540405AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540407AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540266AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540405AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540141AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540262AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540406AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139001.PDS /archive/modis/P15409571540958154095912024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540261AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540342AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540114AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139000.PDS /archive/modis/P15409571540958154095912024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139001.PDS /archive/modis/P1540415AAAAAAAAAAAAAA12024002139001.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:10', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139000.PDS /archive/modis/P1540157AAAAAAAAAAAAAA12024002139000.PDS']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:16', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:17', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:17', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:17', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:17', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:18', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:18', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:18', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:18', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:19', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:20', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:20', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:20', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540290AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:21', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:22', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:22', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:22', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:22', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:23', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:23', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:24', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:25', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:26', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:26', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:26', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:26', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:26', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P1540414AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P1540404AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:27', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:28', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:29', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:29', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:29', body='FILDIS File Dispatch: /data/modis/P1540220AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:29', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139001.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:29', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139000.PDS ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:30', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:30', body='FILDIS File Dispatch: /data/modis/P1540064AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:30', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:30', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:31', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:31', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:32', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:32', body='FILDIS File Dispatch: /data/modis/P1540407AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:32', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:32', body='FILDIS File Dispatch: /data/modis/P1540266AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:33', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:33', body='FILDIS File Dispatch: /data/modis/P1540405AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:34', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:34', body='FILDIS File Dispatch: /data/modis/P1540141AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:34', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:34', body='FILDIS File Dispatch: /data/modis/P1540262AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:35', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:35', body='FILDIS File Dispatch: /data/modis/P1540406AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:35', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:36', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:36', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:36', body='FILDIS File Dispatch: /data/modis/P1540261AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:37', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:37', body='FILDIS File Dispatch: /data/modis/P1540342AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:37', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:38', body='FILDIS File Dispatch: /data/modis/P1540114AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:38', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:38', body='FILDIS File Dispatch: /data/modis/P15409571540958154095912024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:38', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:39', body='FILDIS File Dispatch: /data/modis/P1540415AAAAAAAAAAAAAA12024002139001.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:39', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/modis']
Message[ID='8250', type='2met.filehandler.sink.success', time='24 01 2012 - 00:37:39', body='FILDIS File Dispatch: /data/modis/P1540157AAAAAAAAAAAAAA12024002139000.PDS ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/modis']"""

TEST_DATA_METOP = """Message[ID='0', type='2met.message', time='31 08 2012 - 09:37:23', body='STOPRC Stop reception: Satellite: METOP-A, Orbit number: 30440, Risetime: 2012-08-31 09:21:59, Falltime: 2012-08-31 09:37:23']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/HIRS_HRP_00_M02_20120831092923Z_20120831093704Z_N_O_20120831092938Z /archive/metop/HIRS_HRP_00_M02_20120831092923Z_20120831093704Z_N_O_20120831092938Z']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/AMSA_HRP_00_M02_20120831092920Z_20120831093704Z_N_O_20120831092933Z /archive/metop/AMSA_HRP_00_M02_20120831092920Z_20120831093704Z_N_O_20120831092933Z']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/AVHR_HRP_00_M02_20120831092929Z_20120831093722Z_N_O_20120831092929Z /archive/metop/AVHR_HRP_00_M02_20120831092929Z_20120831093722Z_N_O_20120831092929Z']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/SEMx_HRP_00_M02_20120831092904Z_20120831093632Z_N_O_20120831092941Z /archive/metop/SEMx_HRP_00_M02_20120831092904Z_20120831093632Z_N_O_20120831092941Z']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/HKTM_HRP_00_M02_20120831092926Z_20120831093712Z_N_O_20120831092933Z /archive/metop/HKTM_HRP_00_M02_20120831092926Z_20120831093712Z_N_O_20120831092933Z']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/MHSx_HRP_00_M02_20120831092920Z_20120831093712Z_N_O_20120831092932Z /archive/metop/MHSx_HRP_00_M02_20120831092920Z_20120831093712Z_N_O_20120831092932Z']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/HIRS_HRP_00_M02_20120831092923Z_20120831093704Z_N_O_20120831092938Z ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/HIRS_HRP_00_M02_20120831092923Z_20120831093704Z_N_O_20120831092938Z ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/AMSA_HRP_00_M02_20120831092920Z_20120831093704Z_N_O_20120831092933Z ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/AMSA_HRP_00_M02_20120831092920Z_20120831093704Z_N_O_20120831092933Z ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/HIRS_HRP_00_M02_20120831092923Z_20120831093704Z_N_O_20120831092938Z ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/IASI_HRP_00_M02_20120831092928Z_20120831093721Z_N_O_20120831092929Z /archive/metop/IASI_HRP_00_M02_20120831092928Z_20120831093721Z_N_O_20120831092929Z']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/GOME_HRP_00_M02_20120831092929Z_20120831093721Z_N_O_20120831092930Z /archive/metop/GOME_HRP_00_M02_20120831092929Z_20120831093721Z_N_O_20120831092930Z']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/ASCA_HRP_00_M02_20120831092928Z_20120831093722Z_N_O_20120831092929Z /archive/metop/ASCA_HRP_00_M02_20120831092928Z_20120831093722Z_N_O_20120831092929Z']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/ADCS_HRP_00_M02_20120831092920Z_20120831093704Z_N_O_20120831092937Z /archive/metop/ADCS_HRP_00_M02_20120831092920Z_20120831093704Z_N_O_20120831092937Z']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/GRAS_HRP_00_M02_20120831092931Z_20120831093717Z_N_O_20120831092934Z /archive/metop/GRAS_HRP_00_M02_20120831092931Z_20120831093717Z_N_O_20120831092934Z']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/AMSA_HRP_00_M02_20120831092920Z_20120831093704Z_N_O_20120831092933Z ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/AVHR_HRP_00_M02_20120831092929Z_20120831093722Z_N_O_20120831092929Z ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/AVHR_HRP_00_M02_20120831092929Z_20120831093722Z_N_O_20120831092929Z ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:34', body='FILDIS File Dispatch: /data/metop/SEMx_HRP_00_M02_20120831092904Z_20120831093632Z_N_O_20120831092941Z ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:35', body='FILDIS File Dispatch: /data/metop/SEMx_HRP_00_M02_20120831092904Z_20120831093632Z_N_O_20120831092941Z ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:35', body='FILDIS File Dispatch: /data/metop/HKTM_HRP_00_M02_20120831092926Z_20120831093712Z_N_O_20120831092933Z ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:35', body='FILDIS File Dispatch: /data/metop/HKTM_HRP_00_M02_20120831092926Z_20120831093712Z_N_O_20120831092933Z ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:35', body='FILDIS File Dispatch: /data/metop/MHSx_HRP_00_M02_20120831092920Z_20120831093712Z_N_O_20120831092932Z ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:35', body='FILDIS File Dispatch: /data/metop/AVHR_HRP_00_M02_20120831092929Z_20120831093722Z_N_O_20120831092929Z ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:35', body='FILDIS File Dispatch: /data/metop/MHSx_HRP_00_M02_20120831092920Z_20120831093712Z_N_O_20120831092932Z ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:35', body='FILDIS File Dispatch: /data/metop/SEMx_HRP_00_M02_20120831092904Z_20120831093632Z_N_O_20120831092941Z ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:35', body='FILDIS File Dispatch: /data/metop/HKTM_HRP_00_M02_20120831092926Z_20120831093712Z_N_O_20120831092933Z ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:35', body='FILDIS File Dispatch: /data/metop/MHSx_HRP_00_M02_20120831092920Z_20120831093712Z_N_O_20120831092932Z ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:36', body='FILDIS File Dispatch: /data/metop/IASI_HRP_00_M02_20120831092928Z_20120831093721Z_N_O_20120831092929Z ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:36', body='FILDIS File Dispatch: /data/metop/IASI_HRP_00_M02_20120831092928Z_20120831093721Z_N_O_20120831092929Z ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:37', body='FILDIS File Dispatch: /data/metop/GOME_HRP_00_M02_20120831092929Z_20120831093721Z_N_O_20120831092930Z ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:37', body='FILDIS File Dispatch: /data/metop/ASCA_HRP_00_M02_20120831092928Z_20120831093722Z_N_O_20120831092929Z ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:37', body='FILDIS File Dispatch: /data/metop/GOME_HRP_00_M02_20120831092929Z_20120831093721Z_N_O_20120831092930Z ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:37', body='FILDIS File Dispatch: /data/metop/ADCS_HRP_00_M02_20120831092920Z_20120831093704Z_N_O_20120831092937Z ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:38', body='FILDIS File Dispatch: /data/metop/IASI_HRP_00_M02_20120831092928Z_20120831093721Z_N_O_20120831092929Z ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:38', body='FILDIS File Dispatch: /data/metop/ASCA_HRP_00_M02_20120831092928Z_20120831093722Z_N_O_20120831092929Z ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:38', body='FILDIS File Dispatch: /data/metop/GRAS_HRP_00_M02_20120831092931Z_20120831093717Z_N_O_20120831092934Z ftp://safuser@pps.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:38', body='FILDIS File Dispatch: /data/metop/ADCS_HRP_00_M02_20120831092920Z_20120831093704Z_N_O_20120831092937Z ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:38', body='FILDIS File Dispatch: /data/metop/GOME_HRP_00_M02_20120831092929Z_20120831093721Z_N_O_20120831092930Z ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:38', body='FILDIS File Dispatch: /data/metop/GRAS_HRP_00_M02_20120831092931Z_20120831093717Z_N_O_20120831092934Z ftp://safusr.t@pps2.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:38', body='FILDIS File Dispatch: /data/metop/ASCA_HRP_00_M02_20120831092928Z_20120831093722Z_N_O_20120831092929Z ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:38', body='FILDIS File Dispatch: /data/metop/ADCS_HRP_00_M02_20120831092920Z_20120831093704Z_N_O_20120831092937Z ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/metop']
Message[ID='8250', type='2met.filehandler.sink.success', time='31 08 2012 - 09:37:38', body='FILDIS File Dispatch: /data/metop/GRAS_HRP_00_M02_20120831092931Z_20120831093717Z_N_O_20120831092934Z ftp://safusr.u@safe.smhi.se:21//san1/polar_in/direct_readout/metop']"""


import posttroll.publisher
import posttroll.subscriber

old_stuff = {}
lines = []
class FakePublish(object):
    def __init__(self, *args):
        global lines
        lines = []
    def __enter__(self):
        return self

    def send(self, msg):
        global lines
        lines.append(msg)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def patch_publish():
    old_stuff["Publish"] = posttroll.publisher.Publish
    posttroll.publisher.Publish = FakePublish

def unpatch_publish():
    posttroll.publisher.Publish = old_stuff["Publish"]

patch_publish()


TEST_DATA = []

class FakeSubscriber(object):
    def __init__(self, *args):
        pass
    def recv(self):
        for line in TEST_DATA:
            yield line

def patch_subscriber():
    old_stuff["Subscriber"] = posttroll.subscriber.Subscriber
    posttroll.subscriber.Subscriber = FakeSubscriber

def unpatch_subscriber():
    posttroll.subscriber.Subscriber = old_stuff["Subscriber"]

patch_subscriber()



from receiver import MessageReceiver, TwoMetMessage, receive_from_zmq, Message
from posttroll.message import Message
import unittest
from datetime import datetime

def test_read(test_data):
    """Test reading data.
    """
    lines = test_data.split("\n")
    mr_ = MessageReceiver()
    for line in lines:
        to_send = mr_.receive(TwoMetMessage(line))
        if to_send:
            try:
                to_send["risetime"] = to_send["risetime"].isoformat()
                to_send["falltime"] = to_send["falltime"].isoformat()
            except AttributeError:
                pass
            print to_send
            msg = Message('/oper/polar/direct_readout/norrköping', "file",
                          to_send).encode()
            print "Should publish", msg




class ReceiverTester(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        global TEST_DATA
        TEST_DATA = []
        

    def test_noaa19(self):
        global TEST_DATA
        TEST_DATA = []
        for i in TEST_DATA_NOAA19.split("\n"):
            TEST_DATA.append(Message("/oper/2met!", "2met!", i, False))

        receive_from_zmq(None)

        # {"satellite": "NOAA 19", "format": "16-bit HRPT Minor Frame",
        # "start_time": "2012-01-12T11:19:32", "orbit_number": "15090", "uri":
        # "ssh://nimbus.smhi.se/archive/hrpt/20120112111932_NOAA_19.hmf",
        # "orbit number": "15090", "end_time": "2012-01-12T11:35:20",
        # "filename": "20120112111932_NOAA_19.hmf", "type": "HRPT 0"}

        keys = set(["satellite", "format", "start_time", "end_time", "filename",
                    "uri", "type", "orbit_number"])

        
        for line in lines:
            data = Message(rawstr=line).data
            self.assertEqual(keys, set(data.keys()))
            self.assertEqual(data["satellite"], "NOAA 19")
            self.assertEqual(data["format"], "16-bit HRPT Minor Frame")
            self.assertEqual(data["start_time"],
                             datetime(2012, 1, 12, 11, 19, 32))
            self.assertEqual(data["end_time"],
                             datetime(2012, 1, 12, 11, 35, 20))
            self.assertEqual(data["filename"], "20120112111932_NOAA_19.hmf")
            self.assertEqual(data["type"], "HRPT 0")
            self.assertEqual(data["orbit_number"], 15090)

            
    def test_npp(self):
        global TEST_DATA
        TEST_DATA = []
        for i in TEST_DATA_NPP.split("\n"):
            TEST_DATA.append(Message("/oper/2met!", "2met!", i, False))

        receive_from_zmq(None)

        keys = set(["satellite", "format", "start_time", "end_time", "filename",
                    "instrument", "uri", "type", "orbit_number"])

        
        for line in lines:
            data = Message(rawstr=line).data
            self.assertEqual(keys, set(data.keys()))
            self.assertEqual(data["satellite"], "NPP")
            self.assertEqual(data["format"], "HDF5")
            self.assertEqual(data["start_time"],
                             datetime(2012, 7, 5, 7, 6, 48))
            self.assertEqual(data["end_time"],
                             datetime(2012, 7, 5, 7, 16, 24))
            self.assertTrue(data["filename"] in
                            ["RNSCA-RVIRS_npp_d20120705_t0706492_e0716204_b00001_c20120705071952092000_nfts_drl.h5",
                             'RCRIS-RNSCA_npp_d20120705_t0706508_e0716230_b00001_c20120705071952132000_nfts_drl.h5',
                             'RATMS-RNSCA_npp_d20120705_t0706500_e0715388_b00001_c20120705071952147000_nfts_drl.h5'])
            self.assertEqual(data["type"], "RDR")
            self.assertEqual(data["orbit_number"], 3560)


    def test_terra(self):
        global TEST_DATA
        TEST_DATA = []
        for i in TEST_DATA_TERRA.split("\n"):
            TEST_DATA.append(Message("/oper/2met!", "2met!", i, False))

        receive_from_zmq(None)

        keys = set(["satellite", "format", "start_time", "end_time", "filename",
                    "instrument", "uri", "type", "orbit_number", "number"])

        
        for line in lines:
            data = Message(rawstr=line).data
            self.assertEqual(keys, set(data.keys()))
            self.assertEqual(data["satellite"], "TERRA")
            self.assertEqual(data["format"], "PDS")
            self.assertEqual(data["start_time"],
                             datetime(2012, 1, 23, 21, 57, 43))
            self.assertEqual(data["end_time"],
                             datetime(2012, 1, 23, 22, 10, 25))
            self.assertTrue(data["filename"] in
                            ["P0420064AAAAAAAAAAAAAA12023215743001.PDS",
                             "P0420064AAAAAAAAAAAAAA12023215743000.PDS",
                             "P0420064AAAAAAAAAAAAAA12023215743001.PDS",
                             "P0420064AAAAAAAAAAAAAA12023215743000.PDS",
                             "P0420064AAAAAAAAAAAAAA12023215743001.PDS",
                             "P0420064AAAAAAAAAAAAAA12023215743001.PDS",
                             "P0420064AAAAAAAAAAAAAA12023215743000.PDS",
                             "P0420064AAAAAAAAAAAAAA12023215743000.PDS"])
            self.assertEqual(data["type"], "EOS 0")
            self.assertEqual(data["orbit_number"], 64360)

    def test_aqua(self):
        global TEST_DATA
        TEST_DATA = []
        for i in TEST_DATA_AQUA.split("\n"):
            TEST_DATA.append(Message("/oper/2met!", "2met!", i, False))

        receive_from_zmq(None)

        keys = set(["satellite", "format", "start_time", "end_time", "filename",
                    "instrument", "uri", "type", "orbit_number", "number"])

        
        for line in lines:
            data = Message(rawstr=line).data
            self.assertEqual(keys, set(data.keys()))
            self.assertEqual(data["satellite"], "AQUA")
            self.assertEqual(data["format"], "PDS")
            self.assertEqual(data["start_time"],
                             datetime(2012, 1, 24, 0, 21, 39))
            self.assertEqual(data["end_time"],
                             datetime(2012, 1, 24, 0, 35, 21))
            self.assertTrue(data["filename"] in
                            [
                                "P1540342AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540342AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540064AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540220AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540290AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540141AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540114AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540290AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540261AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540157AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540342AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540404AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540407AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540414AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540415AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540342AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540414AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540404AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540266AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540406AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540220AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540064AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540262AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540405AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540407AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540266AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540405AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540141AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540262AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540406AAAAAAAAAAAAAA12024002139001.PDS",
                                "P15409571540958154095912024002139001.PDS",
                                "P1540261AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540342AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540114AAAAAAAAAAAAAA12024002139000.PDS",
                                "P15409571540958154095912024002139000.PDS",
                                "P1540415AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540157AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540064AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540220AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540064AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540064AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540290AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540141AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540220AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540220AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540114AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540290AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540290AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540290AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540261AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540157AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540141AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540141AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540114AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540114AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540404AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540290AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540290AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540407AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540414AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540261AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540261AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540415AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540414AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540157AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540157AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540404AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540266AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540406AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540220AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540404AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540064AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540404AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540262AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540407AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540405AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540407AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540407AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540414AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540414AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540266AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540415AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540405AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540415AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540141AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540414AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540262AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540414AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540406AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540404AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540404AAAAAAAAAAAAAA12024002139000.PDS",
                                "P15409571540958154095912024002139001.PDS",
                                "P1540266AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540261AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540266AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540342AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540406AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540114AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540406AAAAAAAAAAAAAA12024002139000.PDS",
                                "P15409571540958154095912024002139000.PDS",
                                "P1540220AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540220AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540415AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540157AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540064AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540064AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540262AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540262AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540405AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540405AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540407AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540407AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540266AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540266AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540405AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540405AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540141AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540141AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540262AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540262AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540406AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540406AAAAAAAAAAAAAA12024002139001.PDS",
                                "P15409571540958154095912024002139001.PDS",
                                "P15409571540958154095912024002139001.PDS",
                                "P1540261AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540261AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540342AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540342AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540114AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540114AAAAAAAAAAAAAA12024002139000.PDS",
                                "P15409571540958154095912024002139000.PDS",
                                "P15409571540958154095912024002139000.PDS",
                                "P1540415AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540415AAAAAAAAAAAAAA12024002139001.PDS",
                                "P1540157AAAAAAAAAAAAAA12024002139000.PDS",
                                "P1540157AAAAAAAAAAAAAA12024002139000.PDS",
                                ])
            self.assertEqual(data["type"], "EOS 0")
            self.assertEqual(data["orbit_number"], 51722)
            

    # NOT IMPLEMENTED YET
    # def test_metop(self):
    #     global TEST_DATA
    #     TEST_DATA = []
    #     for i in TEST_DATA_METOP.split("\n"):
    #         TEST_DATA.append(Message("/oper/2met!", "2met!", i, False))

    #     print "*" * 80
    #     receive_from_zmq(None)
    #     print "*" * 80

    #     keys = set(["satellite", "format", "start_time", "end_time", "filename",
    #                 "uri", "type", "orbit_number"])



    #     print lines
        
    #     for line in lines:
    #         data = Message(rawstr=line).data
    #         self.assertEqual(keys, set(data.keys()))
    #         self.assertEqual(data["satellite"], "NOAA 19")
    #         self.assertEqual(data["format"], "16-bit HRPT Minor Frame")
    #         self.assertEqual(data["start_time"],
    #                          datetime(2012, 1, 12, 11, 19, 32))
    #         self.assertEqual(data["end_time"],
    #                          datetime(2012, 1, 12, 11, 35, 20))
    #         self.assertEqual(data["filename"], "20120112111932_NOAA_19.hmf")
    #         self.assertEqual(data["type"], "HRPT 0")
    #         self.assertEqual(data["orbit_number"], 15090)

unpatch_publish()
unpatch_subscriber()

if __name__ == '__main__':

    unittest.main()





    
    #test_read(TEST_DATA_NOAA19)
    #test_read(TEST_DATA_TERRA)
    #test_read(TEST_DATA_AQUA)

# cleaning
# To be filtered out: Message[ID='20300', type='egmc2.action.submitted', time='27 01 2012 - 12:44:19', body='Command 2met.control.limit::clean[[]] has been submitted, current feedback is ${feedback}.']
# New Message: Message[ID='20300', type='egmc2.action.submitted', time='27 01 2012 - 12:44:19', body='Command 2met.control.limit::clean[[]] has been submitted, current feedback is ${feedback}.']
# To be filtered out: Message[ID='8100', type='2met.limit.success', time='27 01 2012 - 12:44:19', body='LIMSUC File LIMIT was called with target clean. Limit Files by Age: checked 4 target directories and deleted 4 files. Limit Files by Counts: checked 2 target directories and deleted 0 files.']
# New Message: Message[ID='8100', type='2met.limit.success', time='27 01 2012 - 12:44:19', body='LIMSUC File LIMIT was called with target clean. Limit Files by Age: checked 4 target directories and deleted 4 files. Limit Files by Counts: checked 2 target directories and deleted 0 files.']
# To be filtered out: Message[ID='20302', type='egmc2.action.finished', time='27 01 2012 - 12:44:19', body='Command 2met.control.limit::clean[[]] has been finished, feedback is FIN [958942024] - code=0, value=Limit Files by Age: checked 4 target directories and deleted 4 files. Limit Files by Counts: checked 2 target directories and deleted 0 files..']
# New Message: Message[ID='20302', type='egmc2.action.finished', time='27 01 2012 - 12:44:19', body='Command 2met.control.limit::clean[[]] has been finished, feedback is FIN [958942024] - code=0, value=Limit Files by Age: checked 4 target directories and deleted 4 files. Limit Files by Counts: checked 2 target directories and deleted 0 files..']

    #import zmq
    #context = zmq.Context()
    #pub = context.socket(zmq.PUB)
    #pub.bind("tcp://*:9331")
    # pub.send("pytroll://oper/2met! 2met! a001673@c13246.ad.smhi.se 2012-09-18T14:18:56.255761 v1.01 text/ascii Message[ID='0', type='2met.message', time='18 09 2012 - 16:18:56', body='STOPRC Stop reception: Satellite: NOAA 19, Orbit number: 18618, Risetime: 2012-09-18 14:07:56, Falltime: 2012-09-18 14:18:56']")

