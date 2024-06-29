# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/5/9 15:10
@Author : karsten
@File : mag_lg_2_event_download.py
@Software: PyCharm
============================
"""
import numpy as np
import pandas as pd
from obspy import UTCDateTime
import os
import subprocess
from datetime import datetime
import glob

################## 数据预处理 ##################
# 读取数据
data_locate = '../../data/sparta_eq_catalog/data_processing.csv'
data = pd.read_csv(data_locate)
# 剔除震级为-的数据
data = data[data['mag'] != '-']
# 转换为float
data['mag'] = data['mag'].astype(float)
data['depth'] = data['depth'].astype(float)
# 选择前2天的数据
data = data[data['Day_interval'] <= 5]
data = data.reset_index(drop=True)
# 保存起来
data.to_csv('../../data/sparta_eq_catalog/day_2_event.csv')
# 打印出来看看
print(data)
# 将data专为numpy方便计算
data_numpy = np.array(data)

################## 给定基础参数 ##################

# 需要下载的事件的时间窗口
time_before_start = 10 # 10s
time_after_start = 4*60 # 4分钟
output_name = '../../data/sparta_af_30_eq/sparta_download.txt'

# 范围
lat_range = 1
lon_range = 1

fetch_data_locate = '../../FetchData'
PZ_locate = '../../../SAC.PZs'

################## 生成下载事件文件 ##################
with open(output_name, "w") as file:
    # 下载事件
    for i in range(len(data_numpy)):
        # 读取时间
        begin_time = UTCDateTime(data_numpy[i, 1])
        start_time = begin_time - time_before_start
        end_time = begin_time + time_after_start
        # eventlocate
        lat = data_numpy[i, 2]
        lon = data_numpy[i, 3]

        # event_name
        t = round(data_numpy[i, 0], 4)
        name = 'sparta' + str(t)
        # 生成fetchdata需要运行的每一行的信息
        fetch_data_line_HH = ('perl ' + '../../FetchData'  + ' -C ' + 'HH*' + ' --lat ' + str(lat - lat_range) + ':' + str(lat + lat_range)
                           + ' --lon ' + str(lon - lon_range) + ':' + str(lon + lon_range) + ' -s ' + str(start_time) + ' -e ' + str(end_time) +
                           ' -o ' + name + '.mseed' + ' -m ' + name + '.metadata' + '\n')
        fetch_data_line_BH = ('perl ' + '../../FetchData' + ' -C ' + 'BH*' + ' --lat ' + str(lat - lat_range) + ':' + str(
            lat + lat_range)
                              + ' --lon ' + str(lon - lon_range) + ':' + str(lon + lon_range) + ' -s ' + str(
                    start_time) + ' -e ' + str(end_time) +
                              ' -o ' + name + '.mseed' + ' -m ' + name + '.metadata' + '\n')
        fetch_data_line = fetch_data_line_HH + fetch_data_line_BH
        # 将fetch_data_line写入文件中
        file.write(fetch_data_line)

################### 生成文件夹并保存结果 #################
output_folder = '../../data/sparta_af_30_eq/sac_data'
os.makedirs(output_folder, exist_ok=True)
i = 0

with open(output_name, 'r') as file:
    for line in file:
        line = line.strip()
        t = round(data_numpy[i//2, 0], 4)
        name = 'sparta' + str(t)
        folder_name = name
        folder_path = os.path.join(output_folder, folder_name)
        print('path:',folder_path)
        # 利用glob读取里面并判断是否有BH开头的文件
        file = glob.glob(os.path.join(folder_path,'data','*BHZ*'))
        if len(file)>0:
            print('file exist. Next')
            i=i+1
            continue
        os.makedirs(folder_path, exist_ok=True)
        subprocess.run(line, shell=True, cwd=folder_path)

        time_obj = datetime.strptime(data_numpy[i//2, 1], "%Y-%m-%dT%H:%M:%S")
        day_of_year = time_obj.timetuple().tm_yday
        ################## 编写shell脚本并运行 ##################
        shell_script = f"""
#!/bin/bash
echo `pwd`
# 基础参数 ################
EVLA={data_numpy[i//2, 2]}
EVLO={data_numpy[i//2, 3]}
EVDP={data_numpy[i//2, 4]}
Y={time_obj.year}
D={day_of_year}
H={time_obj.hour}
M={time_obj.minute}
S={time_obj.second}
# 转换数据 ################
mseed2sac sparta*.mseed -m sparta{round(data_numpy[i//2, 0], 4)}.metadata
mkdir data
mv *SAC data
# 重命名数据 ################
rm -rf data_pre
mkdir data_pre
cd data
sac << EOF
r *.SAC
ch EVLA $EVLA
ch EVLO $EVLO
ch EVDP $EVDP
ch o gmt $Y $D $H $M $S
w over
q
EOF
cp *.SAC ../data_pre/
cd ../data_pre/
taup_setsac -ph P-1,S-3 -evdpkm -model ak135 *.SAC
# 去除仪器响应 ################
sac << EOD
r *SAC
rtr
rmean
rtr
taper
trans from pol s {PZ_locate} to none freq 0.05 0.1 10 150
w over
quit
EOD
"""
        # 将Shell脚本内容写入到一个文件中
        script = os.path.join('./',folder_path,"script.sh")
        with open(script, "w") as file:
            file.write(shell_script)

        # 使用subprocess模块执行Shell脚本
        subprocess.run(["bash", "script.sh"],cwd=folder_path)
        i = i+1
