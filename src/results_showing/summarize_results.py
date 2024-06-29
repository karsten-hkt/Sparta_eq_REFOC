# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/6/28 14:43
@Author : karsten
@File : summarize_results.py
@Software: PyCharm
============================
"""
import os
import pandas as pd
import numpy as np
import glob

# 定义列名
columns = [
    'year', 'month', 'day', 'hour', 'minute', 'second',
    'day_interval', 'latitude', 'longitude', 'depth', 'magnitude',
    'str_avg', 'dpi_avg', 'rak_avg', 'rot_avg_1', 'rot_avg_2', 'nppl',
    'mfrac_1', 'nspr', 'mavg', 'qual', 'prob', 'magap', 'mpgap', 'mfrac_2',
    'stdr'
]

def read_file(file_path):
	data = []
	with open(file_path, 'r') as file:
		for line in file:
			# 按空格分割每行数据
			values = line.split()
			# 将数据转换为对应的类型（可以根据需要调整）
			values = [int(values[0]), int(values[1]), int(values[2]), int(values[3]), int(values[4]), float(values[5]),
                      float(values[6]), float(values[7]), float(values[8]), float(values[9]), float(values[10]),
                      float(values[11]), float(values[12]), int(values[13]), int(values[14]), int(values[15]),
                      int(values[16]), float(values[17]), int(values[18]), float(values[19]), str(values[20]),
                      float(values[21]), float(values[22]), float(values[23]), float(values[24]), float(values[25])]
			data.append(values)
	return pd.DataFrame(data, columns=columns)

file_locate = '../../output/iter1/2020/202008'
file_list = glob.glob(f'{file_locate}/*.focmec')
file_list.sort()
# Create a dictionary to store the results, X  Y  depth  strike  dip  rake  mag  [newX  newY]  [title]
results = pd.DataFrame(columns=['latitude', 'longitude', 'depth', 'strike', 'dip', 'rake','magnitude', 'newX', 'newY', 'id'])
for i,file in enumerate(file_list):
	event_result = read_file(file)
	new_x = 0
	new_y = 0
	id = event_result.loc[0,'day_interval']
	results.loc[i] = [event_result.loc[0,'longitude'], event_result.loc[0,'latitude'],
					  event_result.loc[0,'depth'], event_result.loc[0,'str_avg'],
					  event_result.loc[0,'dpi_avg'], event_result.loc[0,'rak_avg'], event_result.loc[0,'magnitude'],
					  new_x, new_y, id]
results.to_csv('../../output/summarize_results.csv', index=False, header=False, sep=' ')