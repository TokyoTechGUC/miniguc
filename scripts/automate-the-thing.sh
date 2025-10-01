#!/bin/bash
if [ -z "$1" ] ; then 
	echo "Usage ./automate-the-thing.sh {RUN_NUMBER}"
	exit 0
fi
FOLDER_NAME=$(find ~/runs -type d -regex ".*\/0*$1-[^\/]*$" | head -n1);
CURRENT_DIR=$(pwd)
echo "Selected run no.$1 ($FOLDER_NAME)"
echo "Running geogrid"
cd ~/Build_WRF/WPS
rm FILE*
./geogrid.exe
python ~/scripts/edit-data/geogrid.ju.py
echo "Running ungrib and metgrid"
./ungrib.exe
./metgrid.exe
echo "Moving met_em and geo_em files"
python ~/scripts/edit-data/metgrid.ju.py
mv geo_em* met_em* "$FOLDER_NAME"
echo "Running real.exe"
cd $FOLDER_NAME
mpirun -np 1 ./real.exe
echo "Modifying wrfinput and wrfbdy"
python ~/scripts/edit-data/wrfinput.ju.py $1
python ~/scripts/edit-data/wrfbdy.ju.py $1
cd $CURRENT_DIR
