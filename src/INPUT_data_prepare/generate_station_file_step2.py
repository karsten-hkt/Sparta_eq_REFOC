# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/6/27 16:35
@Author : karsten
@File : generate_station_file_step2.py.py
@Software: PyCharm
============================
"""
import glob
import pandas as pd
from obspy import read_inventory

# 读取数据
stationxml_files = glob.glob('../../data/stations/*')
# 目标格式CE  sta HNE  -- Winterhaven - Sheriff Substati   32.73900 -114.63570    40 1999/12/01 3000/01/01       0
station_info = pd.DataFrame(columns=['net', 'sta', 'lat', 'lon', 'elev'])
for i,stationxml_file in enumerate(stationxml_files):
	invs = read_inventory(stationxml_file)
	net = invs[0].code
	sta = invs[0][0].code
	latitude = invs[0][0].latitude
	longitude = invs[0][0].longitude
	elevation = invs[0][0].elevation
	station_info.loc[i] = [net, sta, latitude, longitude, elevation]
# 保存
station_info.to_csv('../../INPUT/station.txt', index=False, header=False, sep=' ')