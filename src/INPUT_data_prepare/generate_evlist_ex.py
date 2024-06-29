# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/6/27 15:41
@Author : karsten
@File : generate_evlist_ex.py.py
@Software: PyCharm
============================
"""
import os
import pandas as pd
import numpy as np

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

evlist_ex = pd.DataFrame(columns=['year', 'month', 'day_interval', 'lat', 'lon', 'depth', 'mag', 'file_locate'])
# 转换数据
for i in range(data.shape[0]):
	year = str(data.loc[i, 'formatted_datetime']).split('-')[0]
	month =  str(data.loc[i, 'formatted_datetime']).split('-')[1]
	day_interval = round(data.loc[i, 'Day_interval'], 4)
	lat = data.loc[i, 'lat']
	lon = data.loc[i, 'lon']
	depth = data.loc[i, 'depth']
	mag = data.loc[i, 'mag']
	file_locate = f'{year}/{year}{month}/{day_interval}'
	evlist_ex.loc[i] = [year, month, day_interval, lat, lon, depth, mag, file_locate]
evlist_ex.to_csv('../../INPUT/evlist_ex', index=False, header=False, sep=' ')
