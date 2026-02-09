#!/bin/bash
if [ -z "$1" ] ; then 
	echo "Usage ./generate-idealized-input.sh {RUN_NUMBER}"
	exit 0
fi
PROJECT_DIR="/home/mok/miniguc"
FOLDER_NAME=$(find "$PROJECT_DIR/runs" -type d -regex ".*\/0*$1-[^\/]*$" | head -n1);
CURRENT_DIR=$(pwd)
echo "Selected run no.$1 ($FOLDER_NAME)"
echo "Running geogrid"
cd "$PROJECT_DIR/Build_WRF/WPS"
rm FILE*
./geogrid.exe
python "$PROJECT_DIR/scripts/edit-data/geogrid.ju.py"
echo "Running ungrib and metgrid"
./ungrib.exe
./metgrid.exe
echo "Moving met_em and geo_em files"
python "$PROJECT_DIR/scripts/edit-data/metgrid.ju.py"
mv geo_em* met_em* "$FOLDER_NAME"
echo "Running real.exe"
cd $FOLDER_NAME
rm wrfinput*
rm wrfbdy*
rm wrfout*
mpirun -np 1 ./real.exe
echo "Modifying wrfinput and wrfbdy"
python "$PROJECT_DIR/scripts/edit-data/wrfinput.ju.py" $1
python "$PROJECT_DIR/scripts/edit-data/wrfbdy.ju.py" $1
cd $CURRENT_DIR
