#!/bin/bash

PPM_SLOPE=0.230
PPM_OFFSET=-13.9

XADC_PATH='/sys/bus/iio/devices/iio:device0'

sum=0
count=0

OFF=`cat $XADC_PATH/in_temp0_offset`
SCL=`cat $XADC_PATH/in_temp0_scale`

secs=20
endTime=$(( $(date +%s) + secs )) # Calculate end time.

while [ $(date +%s) -lt $endTime ]  # Loop until interval has elapsed.
do
	RAW=`cat $XADC_PATH/in_temp0_raw`
	sum=`expr $sum + $RAW`
	count=`expr $count + 1`
done
FORMULA_T_AVG="(($OFF+$sum/$count)*$SCL)/1000.0"
T_AVG=`echo "scale=6;${FORMULA_T_AVG}" | bc`
echo "T_FPGA = ${T_AVG} °C"

FORMULA_PPM="$PPM_SLOPE*$T_AVG+$PPM_OFFSET"
PPM=`echo "scale=3;${FORMULA_PPM}" | bc`
echo "ppm = ${PPM}"
sed -i "s/corr\s\=\s[-0-9.]\+\;/corr = $PPM\;/g" /opt/redpitaya/www/apps/sdr_wspr/write-c2-files.cfg 
