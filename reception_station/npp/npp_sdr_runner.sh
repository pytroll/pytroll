#!/bin/sh

if [ -f /etc/profile.d/smhi.sh ]
then
. /etc/profile.d/smhi.sh
fi

#echo "SMHI MODE = $SMHI_MODE"

if [ $SMHI_DIST == 'linda' ]
then
SMHI_MODE='offline'
fi

#echo "SMHI MODE = $SMHI_MODE"

case $SMHI_MODE in

################################################################################
# UTV

utv)

CSPP_HOME="/local_disk/opt/CSPP/1_1"
CSPP_WORKDIR="/san1/wrk_cspp"
APPL_HOME="${HOME}/usr"
NPP_SDRPROC_CONFIG_DIR="/data/proj/safutv/dev/npp_dev/pytroll/reception_station/etc/"

        ;;

################################################################################
# TEST

test)

        ;;

################################################################################
# PRODUCTION

prod)

        ;;


################################################################################
# OFFLINE

offline)

CSPP_HOME="/local_disk/opt/CSPP/1_1"
APPL_HOME="${HOME}/usr"

        ;;


################################################################################
# Default

*)
echo "No SMHI_MODE set..."

   ;;

esac




export CSPP_HOME
NPP_SDRPROC=${APPL_HOME}
export NPP_SDRPROC
export CSPP_WORKDIR
export NPP_SDRPROC_CONFIG_DIR

source ${CSPP_HOME}/cspp_env.sh

python ${APPL_HOME}/bin/npp_sdr_runner.py

