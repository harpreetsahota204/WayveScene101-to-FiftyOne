#!/bin/bash

# Download the scene metadata
wget https://raw.githubusercontent.com/wayveai/wayve_scenes/main/data/scene_metadata.csv

# Download the Wayve 101 dataset
gdown --folder 1ppM9-ef9NKGNIJFGpkmbIpf6Qg4UKF-w -O wayve_101 --remaining-ok --continue --no-cookies --no-check-certificate

# Change to the wayve_101 directory
cd wayve_101

# Unzip all files in parallel and remove the zip files
find . -name "*.zip" | parallel -j+0 "unzip -q {} && rm {}"

# Change to the WayveScenes101 directory
cd /content/wayve_101/WayveScenes101

# Unzip all files in parallel and remove the zip files
find . -name "*.zip" | parallel -j+0 "unzip -q {} && rm {}"

echo "WayveScenes Downloaded and Extracted Successfully!"