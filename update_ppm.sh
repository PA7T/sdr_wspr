#!/bin/bash
XADC_PATH='/sys/bus/iio/devices/iio:device0'

PPM_SLOPE=0.230
PPM_OFFSET=-13.9

sum=0
count=0

OFF=`cat $XADC_PATH/in_temp0_offset`
SCL=`cat $XADC_PATH/in_temp0_scale`

secs=20
endTime=$(( $(date +%s) + secs )) # Calculate end time.
#for i in {0..100}
while [ $(date +%s) -lt $endTime ]  # Loop until interval has elapsed.
do
	RAW=`cat $XADC_PATH/in_temp0_raw`
	#FORMULA="(($OFF+$RAW)*$SCL)/1000.0"
	#VAL=`echo "scale=6;${FORMULA}" | bc`
	#echo "in_temp0_raw = ${RAW}"
	#echo "in_temp0 = ${VAL} °C"
	sum=`expr $sum + $RAW`
	#echo "sum = ${sum}"
	count=`expr $count + 1`
	#echo ""
done
#echo "sum = ${sum}"
FORMULA_T_AVG="(($OFF+$sum/$count)*$SCL)/1000.0"
T_AVG=`echo "scale=6;${FORMULA_T_AVG}" | bc`
echo "avg in_temp0 = ${T_AVG} °C"

FORMULA_PPM="$PPM_SLOPE*$T_AVG+$PPM_OFFSET"
PPM=`echo "scale=3;${FORMULA_PPM}" | bc`
echo "ppm = ${PPM}"
sed -i "s/corr\s\=\s[-0-9.]\+\;/corr = $PPM\;/g" write-c2-files.cfg 
