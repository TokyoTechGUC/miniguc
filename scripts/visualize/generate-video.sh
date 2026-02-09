#! /bin/bash
SEARCH_STRING="/home/guc/runs/$1*/results/images/*.png"
ffmpeg -framerate 12 -pattern_type glob -i "$SEARCH_STRING" -y \
       	-c:v libx264 -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" out.mp4
