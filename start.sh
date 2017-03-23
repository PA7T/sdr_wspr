#killall wspr-server
#/opt/redpitaya/www/apps/sdr_wspr/wspr-server &

## declare an array with packages to be installed
declare -a arr=("python3-setuptools" "python3-influxdb" "ntp" "parallel" "libfftw3-bin" "libconfig9" "python-geohash")
for i in "${arr[@]}"
do
	echo "$i"
	if [ `dpkg -l | grep $i | awk '{print $1}'` = "ii" ]
		then
			echo installed
		else
			echo installing-now
			apt-get -y install $i
	fi
done
