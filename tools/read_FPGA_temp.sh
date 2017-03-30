#!/bin/bash

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
echo "T_FPGA = ${T_AVG} °C"
