![alt tag](https://raw.githubusercontent.com/PA7T/sdr_wspr/master/info/icon.png)


## Installation on RedPitaya
SSH into your favourite RP board and execute the following commands:
```shell
ssh root@YOUR-RP-IP-ADDRESS
apt-get install python3-setuptools python3-influxdb ntp parallel libfftw3-bin libconfig9
pip3 install python-geohash
cd /opt/redpitaya/www/apps
git clone https://github.com/PA7T/sdr_wspr.git
cd sdr_wspr
make INSTALL_DIR=/opt/redpitaya
reboot
```
As a result you will find a new application call "SDR WSPR" in the browser under http://YOUR-RP-IP-ADDRESS/ .
