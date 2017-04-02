![alt tag](https://raw.githubusercontent.com/PA7T/sdr_wspr/master/info/icon.png)

SDR WSPR is transforms you RedPitaya board into an 8 channel sofware defined radio receiver for WSPR transmissions. THis means you can monitor wspr beacons on 8 channel simultaneously.

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
## Screenshot
![alt tag](https://raw.githubusercontent.com/PA7T/sdr_wspr/master/info/screenshot.png)

