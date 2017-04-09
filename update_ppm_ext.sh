#/bin/bash

# set gps to 10 MHz output
echo -en '\xB5\x62\x06\x31\x20\x00\x00\x01\x00\x00\x32\x00\x00\x00\x04\x00\x00\x00\x80\x96\x98\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x6F\x00\x00\x00\xAB\x50' > /dev/ttyPS1

# measure 10 MHz reference frequency
f_REF="10000000.0"
T1=`/root/read_FPGA_temp.sh 1`
f=`/root/my_counter 24 12e6`
T2=`/root/read_FPGA_temp.sh 1`
DATE=`date +%Y-%m-%d:%H:%M:%S`

# calculate ppm
FORMULA_PPM="(1.0-$f_REF/$f)*1000000.0"
PPM=`echo "scale=9;${FORMULA_PPM}" | bc`

# print result
echo "$DATE $T1 $T2 $f $PPM"
