project=sdr_wspr

cd /opt/redpitaya/www/apps/sdr_wspr/
build_number=`git rev-list HEAD --count`
revision=`git log -n1 --pretty=%h`

make clean
make INSTALL_DIR=/opt/redpitaya

cd /opt/redpitaya/www/apps/
sed -i "s/\(\"version\":\s\"\).*\"/\1$revision\"/g; s/\(\"revision\":\s\"\).*\"/\1$build_number\"/g" $project/info/info.json
zip -r $project/bazaar/$project-0.97-$build_number.zip $project -x $project/src/**\* $project/.git/**\* $project/.gitignore $project/README.md $project/wspr-vars.sh $project/bazaar/**\* $project/.git/ $project/Makefile 
