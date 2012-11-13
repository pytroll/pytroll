#!/bin/sh
# shell script functions for checking the status of the Suomi NPP SDR runner process
#
# Author: Adam Dybbroe
# Date 2012, November 13
#


function process_id_list {
   PROCESS_NAME=$1
   PROC_LIST=$(ps aux | grep -v grep | grep -i "${PROCESS_NAME}" | grep -v 'log' | awk '{print $2}')
   # NB! PROC may be a list   
}

function process_check {
   if [ $# = 2 ] ; then
      PROCESS_NAME=$1
      PROC=$2
   elif [ $# = 3 ] ; then
      PROCESS_NAME=$1
      PROC=$2
      DO_KILL=$3
   else
      echo $*
      echo "function process_check needs two or three arguments"
      echo " process_check process-name proc-id [do-kill]"
      exit 1
   fi
      
   if [[ ! $PROC ]]
   then
      echo "The processes ${PROCESS_NAME} is not running..."
      exit 0
   fi  

   # If the process is active
   if [[ $PROC ]]
   then
      FIND_RESULT=$(find /proc/$PROC -maxdepth 0) 
      if [[ $FIND_RESULT ]] 
      then
	 echo "The process $PROC is running"
	 if [[ $DO_KILL ]]; then
	    echo -e "\t...tries to kill $PROC now"
	 else
	    echo -e "\t...will NOT kill it"
	 fi
	 
	 if [[ $DO_KILL ]]; then
	    kill -9 $PROC
            status=$?
	    if [[ $status == 0 ]]; then
	       echo "Succeeded killing ${PROC}"
	    else
	       echo "Fails killing ${PROC}, terminates program with error code"
	    fi
	 fi
      else 
	 echo "The process $PROC is not active anymore..."
      fi
   fi

}
