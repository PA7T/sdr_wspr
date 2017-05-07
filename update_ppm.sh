#!/bin/bash

#PPM_SLOPE=0.230
#PPM_OFFSET=-13.9

PPM_CORR=(2.43834701278 -0.594171326321 0.0156288737424 -0.000102828417398) # RP-F04E73
#PPM_CORR=(21.7203115882 -1.31943391218 0.0253848516015 -0.000141918752117) # RP-F03BB6


XADC_PATH='/sys/bus/iio/devices/iio:device0'

sum=0
count=0

OFF=`cat $XADC_PATH/in_temp0_offset`
SCL=`cat $XADC_PATH/in_temp0_scale`

if [ -z "$1" ]
then
	echo "No sampling duration supplied. Using 20sec default."
	secs=20
else
	secs="$1"
fi

endTime=$(( $(date +%s) + secs )) # Calculate end time.

while [ $(date +%s) -lt $endTime ]  # Loop until interval has elapsed.
do
	RAW=`cat $XADC_PATH/in_temp0_raw`
	sum=`expr $sum + $RAW`
	count=`expr $count + 1`
done
FORMULA_T_AVG="(($OFF+$sum/$count)*$SCL)/1000.0"
T_AVG=`echo "scale=6;${FORMULA_T_AVG}" | bc`
#echo "T_FPGA = ${T_AVG} °C"

#FORMULA_PPM="$PPM_SLOPE*$T_AVG+$PPM_OFFSET"
FORMULA_PPM="${PPM_CORR[0]} + ${PPM_CORR[1]}*$T_AVG + ${PPM_CORR[2]}*$T_AVG*$T_AVG + ${PPM_CORR[3]}*$T_AVG*$T_AVG*$T_AVG"
PPM=`echo "scale=3;${FORMULA_PPM}" | bc | awk '{printf "%f", $0}'`
#echo "ppm = ${PPM}"
rw
# write average temperature to temporary file
echo "$T_AVG" > /dev/shm/last_T_FPGA
# replace ppm correction value for data acquisition
sed -i "s/corr\s\=\s[-0-9.]\+\;/corr = $PPM\;/g" /opt/redpitaya/www/apps/sdr_wspr/write-c2-files.cfg
