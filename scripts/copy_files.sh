#!/bin/bash

# Create output directory
mkdir -p output/icon_files

# Find and copy icon files
find src -type f -name "*.icon" -exec cp {} output/icon_files/ \;

echo "Icon files have been copied to output/icon_files" 