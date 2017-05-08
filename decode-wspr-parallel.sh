#!/bin/sh
#
# Decoding script, that times recording of wspr transmissions
#
# Author: Clemens Heese / PA7T <pa7t@wsprlive.net>
#         Pavel Demin
#
# GPLv3 
# 

. /opt/redpitaya/www/apps/sdr_wspr/wspr-vars.sh

JOBS=2
NICE=10

RECORDER=/opt/redpitaya/www/apps/sdr_wspr/write-c2-files
CONFIG=/opt/redpitaya/www/apps/sdr_wspr/write-c2-files.cfg

DECODER=/opt/redpitaya/www/apps/sdr_wspr/wsprd
ALLMEPT=ALL_WSPR.TXT

WSPRLIVEPAYLOAD=/dev/shm/wsprlive_payload.txt

cd /dev/shm
#date

#echo "Sleeping ..."

#SECONDS=`date +%S`
#sleep `expr 60 - $SECONDS`

date
TIMESTAMP=`date --utc +'%y%m%d_%H%M'`

echo "Recording ..."

killall -v $RECORDER  > /dev/null 2>&1
$RECORDER $CONFIG

echo "Decoding ..."

#parallel --keep-order --jobs $JOBS --nice $NICE $DECODER -JC 5000 ::: wspr_*_$TIMESTAMP.c2
export HOME=/dev/shm/
parallel --keep-order --jobs $JOBS --nice $NICE $DECODER -w ::: wspr_*_$TIMESTAMP.c2
rm -f wspr_*_$TIMESTAMP.c2

test -n "$CALL" -a -n "$GRID" -a -s $ALLMEPT || exit

echo "Uploading ..."

# sort by highest SNR, then print unique date/time/band/call combinations,
# and then sort them by date/time/frequency
sort -nr -k 4,4 $ALLMEPT | awk '!seen[$1"_"$2"_"int($6)"_"$7] {print} {++seen[$1"_"$2"_"int($6)"_"$7]}' | sort -n -k 1,1 -k 2,2 -k 6,6 -o $ALLMEPT

echo "to wsprlive.net"
#cat $ALLMEPT >> /media/ramdisk/ALL_WSPR_TEST.TXT
/usr/bin/python3 /opt/redpitaya/www/apps/sdr_wspr/wspr-to-influxdb.py -fo $WSPRLIVEPAYLOAD -r $CALL -rl $GRID -rc "$COMMENT" -u $WLID -pw $WLPW -H data.wsprlive.net -p 8086 -fi $ALLMEPT
curl -u $WLID:$WLPW -i -XPOST 'http://data.wsprlive.net:8086/write?db=wspr&precision=s' --data-binary @$WSPRLIVEPAYLOAD  > /dev/null
test $? -ne 0 || rm -f $WSPRLIVEPAYLOAD

#/usr/bin/python3 /opt/redpitaya/www/apps/sdr_wspr/wspr-to-influxdb.py -r $CALL -rl $GRID -rc "$COMMENT" -u $WLID -pw $WLPW -H data.wsprlive.net -p 8086 -fi $ALLMEPT

echo "to wsprnet"

cp $ALLMEPT wspr_spots.txt
cp $ALLMEPT wspr_last.txt
curl -sS -m 8 -F allmept=@$ALLMEPT -F call=$CALL -F grid=$GRID http://wsprnet.org/post > /dev/null

test $? -ne 0 || rm -f $ALLMEPT
echo "done"
