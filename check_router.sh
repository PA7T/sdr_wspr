#!/bin/bash
HOST=$1

/bin/ping -c 4 $HOST &> /dev/null

if ! [ $? -eq 0 ]
then
  /bin/echo "Host $HOST not reachable rebooting ..."
  /sbin/reboot
#else
#  echo 'Host reachable.'
fi
