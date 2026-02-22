#!/bin/bash

wget https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/ -O tmp.txt
test=$(cat tmp.txt | grep -i "gfs\." | awk -F'[><]' '{print $3}'| sed '2p;d')
echo $test > data-date.txt
wget https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/$test -O tmp.txt
test="https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/${test}/00/atmos/"
wget ${test} -O tmp.txt
cat tmp.txt | grep -i '\.pgrb2\.0p25' | grep -v 'idx' | grep -v '\.anl'| awk '!((NR+2)%3)' | sed -n -e '10,30p' | awk -F'[><]' '{print $3}' | xargs -I{} wget ${test}{}
rm tmp.txt
