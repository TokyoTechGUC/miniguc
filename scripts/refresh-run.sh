#!/bin/bash
if [ -z "$1" ] ; then 
	echo "Usage ./refresh-run.sh {RUN_NUMBER}"
	exit 0
fi
FOLDER_NAME=$(find ~/miniguc/runs -type d -regex ".*\/0*$1-[^\/]*$" | head -n1);
CURRENT_DIR=$(pwd)
echo "Selected run no.$1 ($FOLDER_NAME)"
echo "Running real.exe"
cd $FOLDER_NAME
rm wrfinput* wrfbdy* wrfout*
mpirun -np 1 ./real.exe
echo "Modifying wrfinput and wrfbdy"
python ~/miniguc/scripts/edit-data/wrfinput.ju.py $1
python ~/miniguc/scripts/edit-data/wrfbdy.ju.py $1
cd $CURRENT_DIR
