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

CSPP_HOME="/local_disk/opt/CSPP/1_3"
CSPP_WORKDIR="/san1/cspp/work"
APPL_HOME="${HOME}/usr"
#NPP_SDRPROC_LOG_FILE=/san1/cspp/work/npp_sdr_runner.log
NPP_SDRPROC_LOG_FILE="/var/tmp/satsa_log/npp_sdr_runner.log"
#NPP_SDRPROC_CONFIG_DIR="/data/proj/safutv/dev/npp_dev/pytroll/reception_station/npp/etc/"

        ;;

################################################################################
# TEST

test)

CSPP_HOME="/local_disk/opt/CSPP/current"
CSPP_WORKDIR="/san1/cspp/work"
APPL_HOME="/usr/local"
NPP_SDRPROC_LOG_FILE="/var/log/satellit/npp_sdr_runner.log"
NPP_SDRPROC_CONFIG_DIR="/usr/local/etc"

        ;;

################################################################################
# PRODUCTION

prod)

CSPP_HOME="/local_disk/opt/CSPP/current"
CSPP_WORKDIR="/san1/cspp/work"
APPL_HOME="/usr/local"
NPP_SDRPROC_LOG_FILE="/var/log/satellit/npp_sdr_runner.log"
NPP_SDRPROC_CONFIG_DIR="/usr/local/etc"

        ;;


################################################################################
# OFFLINE

offline)

CSPP_HOME="/local_disk/opt/CSPP/1_2"
APPL_HOME="${HOME}/usr"
CSPP_WORKDIR="/local_disk/tmp"
NPP_SDRPROC_LOG_FILE="/local_disk/tmp/npp_sdr_runner.log"
NPP_SDRPROC_CONFIG_DIR="/usr/local/etc"

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
export NPP_SDRPROC_LOG_FILE

source ${CSPP_HOME}/cspp_env.sh

/usr/bin/python ${APPL_HOME}/bin/npp_sdr_runner.py
