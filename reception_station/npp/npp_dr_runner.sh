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
CSPP_WORKDIR="/san1/cspp_work"
APPL_HOME="${HOME}/usr"
POLAR_PREPROC_CONFIG_DIR="${HOME}/dev/npp_pytroll/pytroll/polar_preproc/etc"

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
CSPP_WORKDIR="/san1/cspp_work"

        ;;


################################################################################
# Default

*)
echo "No SMHI_MODE set..."

   ;;

esac




export CSPP_HOME
NPP_LVL1PROC=${APPL_HOME}
export NPP_LVL1PROC
export CSPP_WORKDIR
export POLAR_PREPROC_CONFIG_DIR

source ${CSPP_HOME}/cspp_env.sh

python ${APPL_HOME}/bin/npp_dr_runner.py

