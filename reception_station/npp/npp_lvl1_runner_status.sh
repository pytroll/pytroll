#!/bin/sh
# Script for checking the status of the Suomi NPP SDR runner
#
# Author: Adam Dybbroe
# Date 2012, November 13
#

if [ -f /etc/profile.d/smhi.sh ]
then
. /etc/profile.d/smhi.sh
fi

case $SMHI_MODE in
utv)
   APPLROOT="/data/proj/safutv/usr/bin"

   ;;
test)
   APPLROOT="/usr/local/bin"

   ;;
prod)
   APPLROOT="/usr/local/bin"

   ;;
*)
echo "No SMHI_MODE set..."

   ;;
esac

#. ${APPLROOT}/npp_sdr_check_runner_lib.sh
. ./npp_sdr_check_runner_lib.sh

processname="npp_sdr_runner"

process_id_list ${processname}

#for procid in ${PROC_LIST}
#do
#   echo "PROC: ${procid}"
#   process_check $processname $procid
#done

idx=0
for procid in ${PROC_LIST}
do 
   idx=`expr $idx + 1`
done

if [[ $idx == 2 ]]
then
   echo "$processname is running!"
fi
if [[ $idx == 0 ]]
then
   echo "$processname is NOT running!"
fi

if [[ $idx > 2 ]]
then
   echo "WARNING: More than one process of $processname running!"
   echo "         Please stop the application and start again!"
fi
