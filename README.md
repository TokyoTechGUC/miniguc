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

## Setup
### Installation
* Check out the guide on how to install WRF and WPS [here](https://github.com/TokyoTechGUC/miniguc/wiki/WRF).
    * Ideally, you might want to name the user as `guc` for compatibility of some hard-coded values in the python scripts (sorry for the design flaw).
* On the home directory (`~`) of the machine, you can clone this repository as a `script` directory
```
cd ~
git clone https://github.com/TokyoTechGUC/miniguc.git scripts
```
* Create two directories `modified-files` and `results` in the home directory to contain the modified input and visualization results from the scripts respectively.
```
cd ~
mkdir modified-files
mkdir results
```

## Script Details
* `download-data`: contains a script to download real-time geographical data, the downloaded data should show up in the directory along with the data date shown on `download-log.txt`. The default number of data files is 30 files containing from 0-hour prediction to 90-hour prediction with 3 hour interval between data.
* `edit-data`: contain a python script to edit `geo_em`, `met_em`, `wrfinput`, and `wrfbdy`. The `geogrid` and `metgrid` script find the data directly on the `wps` directory, while `wrfinput` and `wrfbdy` you need to specify the run id named in the `runs` folder (see Best Practices section).
* `visualize`: contains all necessary scripts for visualizing data
    * `wrf-python-visualization` and `simple-visualization`: contains scripts for python visualization using `matplotlib` module, `wrf-python` module is required for `wrf-python-visualization` scripts. The scripts used `.ju.py` extension, which you can convert it to `.ipynb` using [jupynium](https://github.com/kiyoon/jupynium.nvim).
    * `generate-video.sh` and other shell scripts: a script to call `ffmpeg` to create a video from multiple plot images.
* `generate-idealized-run.sh`: a script to automate the process of generating files in WPS, modify `geo_em` and `met_em` files, generate data in WRF, and modify `wrfinput` and `wrfbdy`. All generated files are moved into its simulation folder. To call it, you can use
```
./generate-idealized-run.sh {run_id}
```
* `refresh-run.sh`: a script to remove and regenerate `wrfbdy` and `wrfinput` files of that run, along with re-modify the files according to scripts in `scripts/edit-data`.
```
./refresh-run.sh {run_id}
```
* `run-multiple.sh`: a script to continuously run and time multiple simulations. In order to use it, you have to modify `ID_LIST` variable in the files with your preferred run IDs. For example, if you want to run a simulation `runs/001-test-run`, `runs/019-ahe-100`, `runs/029-z0-1`, you have to modify `ID_LIST` as `(1 19 29)`. Then, you can simply call `./run-multiple.sh` and everything should start working assuming you have all the necessary files. Running on `tmux` is recommended.
* `open-jupyter.sh`: a script to host a jupyter notebook for the machine. Check out the command to SSH tunnel this jupyter in the useful commands section [here](https://github.com/TokyoTechGUC/miniguc/wiki/Commands)
* `namelists`: not really related to the scripts, but I put it here as a sample namelist configuration for WPS and WRF simulation runs. This is important to replicate a runtime performance from the experiment.

## Best Practices
* Follow the same directory structure as [the installation guide](https://github.com/TokyoTechGUC/miniguc/wiki/WRF). To be more specific, the compatible directory structure for this script is shown as follows
```
/home/guc
├── data
├── libraries
├── models
│   ├── real
│   └── ... (other models)
├── modified-files
├── results
├── runs
│   ├── run-template
│   └── ... (other simulations)
├── scripts (this repository)
├── tests
├── tmp
├── wps
├── wps-geog
└── wrf
```
However, it is also possible to modify the scripts to call from the correct directory as well. This is more of a personal preferences.

* In `runs` directory, it is preferred to refer the run by its ID, i.e. the naming convention is `{id}-{run_name}`. For example, `001-test-run`, `084-grassland-modified-ahe`.

## Side Note
A virtualbox of this mini PC WRF model is saved in an SSD of GUC laboratory, please feel free to check it out. 

The `README` file is provided in this [wiki](https://github.com/TokyoTechGUC/miniguc/wiki/VirtualBox) as well.
