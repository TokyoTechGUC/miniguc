#! /bin/bash
SEARCH_STRING="/home/guc/runs/$1*/results/images/*.png"
ffmpeg -framerate 15 -pattern_type glob -i "$SEARCH_STRING" -y \
       	-c:v libx264 -pix_fmt yuv420p out.mp4
