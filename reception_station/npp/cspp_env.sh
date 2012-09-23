#!/bin/sh
# $Id: cspp_env.sh 857 2012-07-25 13:32:09Z scottm $
# Environment script for CSPP / ADL 3.1.


test -n "$CSPP_HOME" || echo "CSPP_HOME is not set. Please set this environment variable to the install location of CSPP software packages. (When installed, \$CSPP_HOME/ADL is a directory.)"

test -d "$CSPP_HOME/ADL" || echo "CSPP_HOME does not appear to be set properly. See cspp_env.sh"

# revision string for this CSPP release, which we set if we have reasonable expectation that environment is correct
test -d "$CSPP_HOME/ADL" && export CSPP_REV="20120215"


#
# derived CSPP default locations (site installs may move these under some circumstances)
#

# read-write directory into which new ancillary data can be downloaded
export CSPP_ANC_CACHE_DIR=${CSPP_HOME}/cache

# read-write directory for initial SDR luts and download SDR luts
export CSPP_SDR_LUTS=${CSPP_ANC_CACHE_DIR}/luts

# static ancillary data including default algorithm settings
export CSPP_ANC_HOME=${CSPP_HOME}/static

# default location of static ancillary tiles, which we use in-place rather than linking into workspace
export CSPP_ANC_TILE_PATH=${CSPP_ANC_HOME}/ADL/data/tiles/Terrain-Eco-ANC-Tile/withMetadata


#
# user path environment settings, making it easy to invoke wrapper scripts
#

export PATH=${CSPP_HOME}/viirs/sdr:$PATH
export PATH=${CSPP_HOME}/viirs/edr:$PATH
export PATH=${CSPP_HOME}/cris/sdr:$PATH
export PATH=${CSPP_HOME}/atms/sdr:$PATH
export PATH=${CSPP_HOME}/common:$PATH
export PATH=${CSPP_HOME}/common/ShellB3/bin:$PATH


#
# ADL environment settings
#

# location of ADL, which is used by ADL executable configuration files
export ADL_HOME=${CSPP_HOME}/ADL

# set the launch base-time for NPP
export NPP_GRANULE_ID_BASETIME=1698019234000000
#PRE-launch - ADL3.1 test data
#export NPP_GRANULE_ID_BASETIME=1300968033000000

# IET time ancillary used by ADL
export DSTATICDATA=${ADL_HOME}/CMN/Utilities/INF/util/time/src

# DPE domain and site id, used in HDF5 filenames
export DPE_SITE_ID=cspp
export DPE_DOMAIN=dev

# mystery variable is a variable of mystery.
export INFTK_DM_ROOT="JUST_NEED_TO_HAVE_AN_ENV_VARIABLE"
