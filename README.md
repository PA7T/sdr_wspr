![alt tag](https://raw.githubusercontent.com/PA7T/sdr_wspr/master/info/icon.png)

SDR WSPR transforms your [RedPitaya](http://redpitaya.com/) board into an 8 channel sofware defined radio receiver for WSPR transmissions. This means you can monitor wspr beacons on 8 channel simultaneously and report them to [wsprnet.org](http://wsprnet.org/) and [WSPRlive.net](https://wsprlive.net/).

The RedPitaya app is 100% based on the [sdr_transceiver_wspr](http://pavel-demin.github.io/red-pitaya-notes/sdr-transceiver-wspr/) bitstream Pavel Demin has created. Many thanks for such a great piece of work and dedication to the community!

In case you have bug reports or feature requests, please report them as an issue with this GitHub repository. This allows efficient tracking and avoids duplication.

## Installation on RedPitaya
SSH into your favourite RP board with operating system >=0.97 and execute the following commands:
```shell
ssh root@YOUR-RP-IP-ADDRESS
apt-get install python3-setuptools python3-influxdb ntp parallel libfftw3-bin libfftw3-dev libconfig9 libconfig-dev
pip3 install python-geohash
cd /opt/redpitaya/www/apps
rw
git clone https://github.com/PA7T/sdr_wspr.git
cd sdr_wspr
make INSTALL_DIR=/opt/redpitaya
reboot
```
As a result you will find a new application call "SDR WSPR" in the browser under http://YOUR-RP-IP-ADDRESS/ .

## Update to current version
You can always update to the current version via:
```shell
ssh root@YOUR-RP-IP-ADDRESS
cd /opt/redpitaya/www/apps/sdr_wspr
rw
git pull
make clean
make INSTALL_DIR=/opt/redpitaya
reboot
```
## Enable oscillator frequency correction via 1-PPS signal
To enable the new pps-correction feature supported by Pavel's bitstream perform the following additional steps:
connect a 1-pps signal to DIO3_N
```shell
echo "ENABLE_PPM_PPS=true" >> /opt/redpitaya/www/apps/sdr_wspr/wspr-vars.sh
```

## Enable GPSD clock source
First cnnect a GPS receiver to the serial port.
```shell
apt-get -y install gpsd-clients gpsd gpsd-clients
```
Edit /etc/default/gpsd with you favorite editor and make sure it contains the following:
```shell
# Devices gpsd should collect to at boot time.
# They need to be read/writeable, either by user gpsd or the group dialout.
DEVICES="/dev/ttyPS1"

# Other options you want to pass to gpsd
GPSD_OPTIONS="-n"
```

Edit /etc/ntp.conf with you favorite editor and add the following lines:
```shell
# GPS Serial data reference
server 127.127.28.0 minpoll 4 maxpoll 4
fudge 127.127.28.0 time1 0.215 refid GPS
```

## Screenshot
![alt tag](https://raw.githubusercontent.com/PA7T/sdr_wspr/master/info/screenshot.png)

