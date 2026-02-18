# WRF Setup for Mini PC

**Research title**: Development of Small-Scale WRF "Urban" Model for Educational and Research Purposes

**Author**: Mok Wattanasopon and Alvin C. G. Varquez

**Project Report**: [Google Drive](https://drive.google.com/file/d/1M1c2tJbW2_1ucP7tviHG4ANNv81H-fVp/view?usp=sharing)

**Presentation Slides**: [Google Drive](https://drive.google.com/file/d/1rjtzaVJYwyH0ASkUkk031Y1sGFeKTb3L/view?usp=sharing)

## Background
This repository is created as a part of undergraduate Independent Research Project (IRP) of [Global Urban Climatology](https://www.tse.ens.titech.ac.jp/~varquez/en/) laboratory, Institute of Science Tokyo (formerly Tokyo Institute of Technology).

The purpose of this project is to create a small scale environment of [Weather Research and Forecasting (WRF)](https://github.com/wrf-model/WRF) model to simulate various idealized condition, and provide more accessible option of climate simulation study in research institutions.

## Preview
<p align="center">
   <img src="https://github.com/user-attachments/assets/93319dad-67d1-43d4-941f-c068754e1263" width="400">
</p>
<p align="center">A vertical cross-section plot of idealized grassland with urban area in the middle, created and ran using this model</p>

## Setup (To be updated)
### Installation
* Clone this repository with sub modules
```
git clone --recurse-submodules git@github.com:TokyoTechGUC/miniguc.git
```
* Test system environment following [this](https://github.com/TokyoTechGUC/miniguc/wiki/WRF#system-environment-tests) instruction. The test files are already provided in `/TESTS` directory. You only need to install `gfortran` and `csh` (or compilers corresponding to your CPU)
* Install all required libraries in `Build_WRF/LIBRARIES`, following the [instruction](https://github.com/TokyoTechGUC/miniguc/wiki/WRF#building-libraries)
* Test the libraries again following [this instruction](https://github.com/TokyoTechGUC/miniguc/wiki/WRF#library-compatibility-tests)
* Copy the directory `Build_WRF/source` to `Build_WRF/models/real`. This directory is to manage multiple models in case you want to compile different model type or modify the code of the model. Note that you can name the directory however you want
```
cp -r Build_WRF/source Build_WRF/models Build_WRF/models/real
```
* Compile the model in `Build_WRF/models/real` (or the directory that you named) following [this instruction](https://github.com/TokyoTechGUC/miniguc/wiki/WRF#building-wrf)
* Build WPS in `Build_WRF/WPS` following [this instruction](https://github.com/TokyoTechGUC/miniguc/wiki/WRF#building-wps)
* Download the static geography data. You can go to `scripts/` and edit the *last line* of `get-data.sh` to point to `Build_WRF/DATA` directory in your project
    * Make sure to edit `geog_data_paht` in `Build_WRF/WPS/namelist.wps` as shown in [this instruction](https://github.com/TokyoTechGUC/miniguc/wiki/WRF#static-geography-data)
* Go to `runs/run-template` and make a symlink to any files that are required (absolute path is recommended)
```
ln -sf ../../Build_WRF/models/real/phys/noahmp/parameters/MPTABLE.TBL MPTABLE.TBL
ln -sf ../../Build_WRF/models/real/main/ndown.exe ndown.exe
ln -sf ../../Build_WRF/models/real/main/real.exe real.exe
ln -sf ../../Build_WRF/models/real/main/tc.exe tc.exe
ln -sf ../../Build_WRF/models/real/main/wrf.exe wrf.exe
```
### Running the Model
* Copy `run-template` into a new file. The naming convention is `<3 digit number>-<name>-<separated>-<by>-<dashes>`, e.g. `001-my-first-run`, `032-seabreeze-urban-reduced-ahe`, etc.
* Set `Build_WRF/WPS/namelist.wps` and `runs/<your-run-name>/namelist.input` to match what you want to run. Mostly it would be simulation date and number of days
* Check the variables you want to modify in `scripts/edit-data/*.ju.py`. If you want to know how each file works, you can check [this wiki](https://github.com/TokyoTechGUC/miniguc/wiki/Modification)
* Then, you can use the automated script to run everything from WPS to WRF setup
```
script/automate-the-thing.sh <your-run-number>
```
For example, if you want to run WPS, modify the data, and send it to run `001-my-first-run`, you can run
```
script/automate-the-thing.sh 1
```
* You can then move to the run directory and run
```
mpirun -np <cpu core number> ./wrf.exe
```
e.g. I use 14 cores for my run, so I run
```
mpirun -np 14 ./wrf.exe
```
* The script file `do-everything.sh` also give a rough template if you want to run multiple runs in succession.

## Directory Structure
