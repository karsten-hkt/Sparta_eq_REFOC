# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/6/27 15:53
@Author : karsten
@File : generate_locfile.py
@Software: PyCharm
============================
"""
import numpy as np
import pandas as pd
import os
import datetime
def time_delta(time, start_time, datetimeFormat):
	#传入时间行
	#最终将输出时间间隔，以天为单位
	#默认格式为 '2019-07-06T03:19:52.260'
	diff_days = []
	for time_str in time.astype(str):
		diff = datetime.datetime.strptime(time_str, datetimeFormat) - datetime.datetime.strptime(start_time, datetimeFormat)
		diff_days.append(diff.days + diff.seconds / 24 / 60 / 60)

	return diff_days

# 读取数据
data_locate = '../../data/sparta_eq_catalog/supplementary_data1_relocated_catalog_sparta.txt'
df = pd.read_csv(data_locate, sep='\s+', header=None, names=["ID", "YYYY", "MM", "dd", "hh", "mm", "ss.sss", "lat", "lon", "depth", "mag", "ex", "ey", "ez", "et", "rms"])
df['datetime'] = pd.to_datetime(df['YYYY'].astype(str) + '-' + df['MM'].astype(str) + '-' +
								df['dd'].astype(str) + ' ' + df['hh'].astype(str) + ':' + df['mm'].astype(str) +
								':' + df['ss.sss'].astype(str))
# 按要求的格式输出时间
df['formatted_datetime'] = df['datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
#计算时间间隔
start_time = '2020-08-09T12:07:37'
datetimeFormat = '%Y-%m-%dT%H:%M:%S'
diff_days = time_delta(df.loc[:,'formatted_datetime'], start_time, datetimeFormat)
df.insert(0,'Day_interval',diff_days)
df = df[df['Day_interval']>=0]
df = df[df['depth']>0]
df = df.sort_values(by=['Day_interval'],ascending=True)
# 剔除震级为-的数据
df = df[df['mag'] != '-']
# 转换为float
df['mag'] = df['mag'].astype(float)
df['depth'] = df['depth'].astype(float)
df = df[df['Day_interval'] <= 5]
df = df.reset_index(drop=True)

# 生成格式
# 2019 01 01 01 03 37.750  73128971  38.80992 -122.82916   2.983  1.06   0.000   0.000   0.000   0.000   1d
locfile = pd.DataFrame(columns=['year', 'month', 'day', 'hour', 'minute', 'second', 'day_interval', 'lat', 'lon', 'depth', 'mag', 'ex', 'ey', 'ez', 'et', 'velocity_model'])
for i in range(df.shape[0]):
	year = df.loc[i, 'YYYY']
	month = df.loc[i, 'MM']
	day = df.loc[i, 'dd']
	hour = df.loc[i, 'hh']
	minute = df.loc[i, 'mm']
	second = df.loc[i, 'ss.sss']
	day_interval = round(df.loc[i, 'Day_interval'], 4)
	lat = df.loc[i, 'lat']
	lon = df.loc[i, 'lon']
	depth = df.loc[i, 'depth']
	mag = df.loc[i, 'mag']
	ex = 0.000
	ey = 0.000
	ez = 0.000
	et = 0.000
	velocity_model = '1d'
	locfile.loc[i] = [year, month, day, hour, minute, second, day_interval, lat, lon, depth, mag, ex, ey, ez, et, velocity_model]
locfile.to_csv('../../INPUT/sparta_relocation.txt', index=False, header=False, sep=' ')