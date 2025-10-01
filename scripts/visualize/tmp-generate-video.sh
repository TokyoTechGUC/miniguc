#! /bin/bash
SEARCH_STRING="/home/guc/tmp/*.png"
ffmpeg -framerate 15 -pattern_type glob -i "$SEARCH_STRING" -y \
       	-c:v libx264 -pix_fmt yuv420p out.mp4
