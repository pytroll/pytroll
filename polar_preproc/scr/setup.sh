#
# CSPP
#
CSPP_HOME=/usr/local/CSPP
export CSPP_HOME
. $CSPP_HOME/cspp_env.sh

alias dropit=/opt/bin/dropit

PATH=$(dropit -sfep"$PATH" /opt/bin)
PATH=$(dropit -sfep"$PATH" /usr/local/jdk7/bin)

# test
PYTHONPATH=$(dropit -sfep"$PYTHONPATH" /home/ras/dvl/gt/pyorbital)
PYTHONPATH=$(dropit -sfep"$PYTHONPATH" /home/ras/dvl/libpy_npp)

PYTHONPATH=$(dropit -sfep"$PYTHONPATH" /opt/lib/python2.6/site-packages)

export PATH PYTHONPATH

NPP_DATA_DIR='/data/npp'
NPP_WRK_DIR="$NPP_DATA_DIR/work"
NPP_LV0_DIR="$NPP_DATA_DIR/level0"
NPP_LV1_DIR="$NPP_DATA_DIR/level1"
NPP_LV2_DIR="$NPP_DATA_DIR/level2"
PPP_CONFIG_DIR='/opt/etc/mipp'

export NPP_DATA_DIR NPP_WRK_DIR NPP_LV0_DIR NPP_LV1_DIR NPP_LV2_DIR 
export PPP_CONFIG_DIR

