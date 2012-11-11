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

CSPP_HOME="/local_disk/opt/CSPP/1_2"
CSPP_WORKDIR="/san1/cspp/work"
APPL_HOME="${HOME}/usr"
#NPP_SDRPROC_CONFIG_DIR="/data/proj/safutv/dev/npp_dev/pytroll/reception_station/npp/etc/"

        ;;

################################################################################
# TEST

test)

CSPP_HOME="/local_disk/opt/CSPP/current"
CSPP_WORKDIR="/san1/cspp/wrk"
APPL_HOME="/usr"

        ;;

################################################################################
# PRODUCTION

prod)

CSPP_HOME="/local_disk/opt/CSPP/current"
CSPP_WORKDIR="/san1/cspp/wrk"
APPL_HOME="/usr"

        ;;


################################################################################
# OFFLINE

offline)

CSPP_HOME="/local_disk/opt/CSPP/1_2"
APPL_HOME="${HOME}/usr"
CSPP_WORKDIR="/local_disk/tmp"

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
#export NPP_SDRPROC_CONFIG_DIR

source ${CSPP_HOME}/cspp_env.sh

python ${APPL_HOME}/bin/npp_sdr_runner.py
