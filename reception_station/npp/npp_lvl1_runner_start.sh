#!/bin/sh
# Script for starting the Suomi NPP SDR runner
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
   PYTHONPATH="/usr/local/lib64/python2.6/site-packages:/usr/local/lib/python2.6/site-packages"
   PYTHONPATH="${PYTHONPATH}:/data/proj/safutv/usr/lib/python2.6/site-packages:/data/proj/safutv/usr/lib64/python2.6/site-packages"

   ;;
test)
   APPLROOT="/usr/local/bin"
   PYTHONPATH="/usr/local/lib64/python2.6/site-packages:/usr/local/lib/python2.6/site-packages"

   ;;
prod)
   APPLROOT="/usr/local/bin"
   PYTHONPATH="/usr/local/lib64/python2.6/site-packages:/usr/local/lib/python2.6/site-packages"

   ;;
*)
echo "No SMHI_MODE set..."

   ;;
esac

. ${APPLROOT}/npp_sdr_check_runner_lib.sh
export PYTHONPATH

processname="npp_sdr_runner"

process_id_list ${processname}

idx=0
for procid in ${PROC_LIST}
do 
   idx=`expr $idx + 1`
done

if [[ $idx == 2 ]]
then
   echo "$processname already running!"
fi
if [[ $idx == 0 ]]
then
   echo "Starting $processname"
   nohup ${APPLROOT}/npp_sdr_runner.sh > /dev/null 2>&1 &
fi

if [[ $idx > 2 ]]
then
   echo "WARNING: More than one process of $processname running!"
   echo "         Please stop the application and start again!"
fi
