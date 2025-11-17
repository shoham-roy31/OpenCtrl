#!/bin/bash
FOLDERS=("dist" "build")
echo "Running pre-build script..."
echo "Starting pre-build cleanup..."
echo "Cleaning up previous builds..."
for folder in "${FOLDERS[@]}"; do
    if [ -d "$folder" ]; then
        echo "Removing $folder..."
        rm -rf "$folder"
    fi
source OpenCtrl/Script/activate
python setup.py sdist bdist_wheel
echo "Build completed."
done