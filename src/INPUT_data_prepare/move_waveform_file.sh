#!/bin/bash

# This script moves waveform files from the original directory to the new directory
cd ../../data/sparta_af_30_eq/sac_data/
file=$(ls)
for filename in $file
do
    cd $filename
    # 只要后面的数字
    name=$(echo $filename | sed 's/sparta//g')
    mkdir ../../../../INPUT/WAVEFORM/2020/202008/$name
    cp ./rotate/* ../../../../INPUT/WAVEFORM/2020/202008/$name
    cd ..
done