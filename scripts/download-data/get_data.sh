#!/bin/bash

wget https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/ -O temp0.txt
test=$(cat temp0.txt | grep -i "gfs\." | awk -F'[><]' '{print $3}'| sed '2p;d')
echo $test > download-log.txt
wget https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/$test -O temp0.txt
# test=$(cat temp0.txt | grep -i 'href'| awk -F'[><]' '{print $3}'| tail -n 1 | xargs -I{} echo https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/${test}{}atmos/)
test="https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/${test}/00/atmos/"
wget ${test} -O temp0.txt
cat temp0.txt | grep -i '\.pgrb2\.0p25' | grep -v 'idx' | grep -v '\.anl'| awk '!((NR+2)%3)' | sed -n -e '10,30p' | awk -F'[><]' '{print $3}' | xargs -I{} wget ${test}{}
mv gfs* /home/guc/Build_WRF/DATA/
