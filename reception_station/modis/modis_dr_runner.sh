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

SPA_HOME="/local_disk/opt/MODISL1DB_SPA/current"
APPL_HOME="${HOME}/usr"
MODIS_LVL1PROC_LOG_FILE="/var/tmp/satsa_log/modis_lvl1proc.log"

        ;;

################################################################################
# TEST

test)

SPA_HOME="/local_disk/opt/MODISL1DB_SPA/current"
APPL_HOME="/usr/local"
MODIS_LVL1PROC_LOG_FILE="/var/log/satellit/modis_lvl1proc.log"
MODIS_LVL1PROC_CONFIG_DIR="/usr/local/etc"

        ;;

################################################################################
# PRODUCTION

prod)

SPA_HOME="/local_disk/opt/MODISL1DB_SPA/current"
APPL_HOME="/usr/local"
MODIS_LVL1PROC_LOG_FILE="/var/log/satellit/modis_lvl1proc.log"
MODIS_LVL1PROC_CONFIG_DIR="/usr/local/etc"

        ;;


################################################################################
# OFFLINE

offline)

SPA_HOME="/local_disk/opt/SPA"
APPL_HOME="${HOME}/usr"

        ;;


################################################################################
# Default

*)
echo "No SMHI_MODE set..."

   ;;

esac


export SPA_HOME
export MODIS_LVL1PROC_LOG_FILE
export MODIS_LVL1PROC_CONFIG_DIR

MODIS_LVL1PROC=${APPL_HOME}
export MODIS_LVL1PROC
python ${APPL_HOME}/bin/modis_dr_runner.py
