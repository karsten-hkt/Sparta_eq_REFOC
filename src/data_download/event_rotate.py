# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/6/24 17:02
@Author : karsten
@File : event_rotate.py
@Software: PyCharm
============================
"""
import glob
import os
import subprocess

# sac_data所在的文件夹
sac_file = '../../data/sparta_af_30_eq/sac_data'

# 读取所有的目录
events = glob.glob(os.path.join(sac_file, '*'))
for event in events:
	# 路径
	folder_path =event
	print(folder_path)
	# 构建一个脚本，旋转事件
	rotate_script = f'''
#!/bin/bash
rm -rf rotate
mkdir rotate

cd ./data_pre/
file_HE=$(ls *HHE*)
file_BE=$(ls *BHE*)
file_H1=$(ls *HH1*)
file_B1=$(ls *BH1*)

#对HE台站
for filename in $file_HE
do
N_HE=$(echo $filename | sed 's/HHE/HHN/g')
Z_HE=$(echo $filename | sed 's/HHE/HHZ/g')
R_HE=$(echo $filename | sed 's/HHE.*.SAC/r/g')
T_HE=$(echo $filename | sed 's/HHE.*.SAC/t/g')
Z_HE_z=$(echo $filename | sed 's/HHE.*.SAC/z/g')

sac << EOD
cut o -5 180
r $N_HE $filename
rotate to gcp
w $R_HE $T_HE
cut o -5 180
r $Z_HE
w $Z_HE_z

quit
EOD
done

# 对BE台站
for filename in $file_BE
do
Z_BE=$(echo $filename | sed 's/BHE/BHZ/g')
N_BE=$(echo $filename | sed 's/BHE/BHN/g')

R_BE=$(echo $filename | sed 's/BHE.*.SAC/r/g')
T_BE=$(echo $filename | sed 's/BHE.*.SAC/t/g')
Z_BE_z=$(echo $filename | sed 's/BHE.*.SAC/z/g')

sac << EOD
cut o -5 180
r $N_BE $filename
rotate to gcp
w $R_BE $T_BE
cut o -5 180
r $Z_BE
w $Z_BE_z

quit
EOD

done

#对H1台站
for filename in $file_H1
do
E_H1=$(echo $filename | sed 's/HH1/HH2/g')
Z_H1=$(echo $filename | sed 's/HH1/HHZ/g')
R_H1=$(echo $filename | sed 's/HH1.*.SAC/r/g')
T_H1=$(echo $filename | sed 's/HH1.*.SAC/t/g')
Z_H1_Z=$(echo $filename | sed 's/HH1.*.SAC/z/g')

sac << EOD
cut o -5 180
r $filename $E_H1
rotate to gcp
w $R_H1 $T_H1
cut o -5 180
r $Z_H1
w $Z_H1_Z

quit
EOD
done

#对B1台站
for filename in $file_B1
do
E_B1=$(echo $filename | sed 's/BH1/BH2/g')
Z_B1=$(echo $filename | sed 's/BH1/BHZ/g')
R_B1=$(echo $filename | sed 's/BH1.*.SAC/r/g')
T_B1=$(echo $filename | sed 's/BH1.*.SAC/t/g')
Z_B1_Z=$(echo $filename | sed 's/BH1.*.SAC/z/g')

sac << EOD
cut o -5 180
r $filename $E_B1
rotate to gcp
w $R_B1 $T_B1
cut o -5 180
r $Z_B1
w $Z_B1_Z

quit
EOD
done

mv *r *t *z ../rotate
cd ../rotate
taup setsac -ph p-1,P-1,s-3,S-3 -evdpkm -model ak135 *
'''
	# 将Shell脚本内容写入到一个文件中
	script = os.path.join('./', folder_path, "rotate.sh")
	with open(script, "w") as file:
		file.write(rotate_script)

	# 使用subprocess模块执行Shell脚本
	subprocess.run(["bash", "rotate.sh"], cwd=folder_path)
