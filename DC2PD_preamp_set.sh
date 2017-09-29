#!/bin/sh

if [ "$#" -lt  "2" ]
then
        echo "No arguments supplied"
else
        CHIPADDRESS=$1
        dB=$2
	
        echo "Setting DC2PD preamplifier at address $CHIPADDRESS to $dB dB gain."
	
	DAC=`echo "(4095 * ($dB - 7.5))/(55.5 - 7.5)" | bc`

        HIGHBYTE=`echo $(($DAC >> 4))`
        LOWBYTE=`echo $((($DAC << 4) & 255))`

        i2cset -y 0 $CHIPADDRESS 0x60 $HIGHBYTE $LOWBYTE i # write 3000 to DAC & EEPROM
fi

