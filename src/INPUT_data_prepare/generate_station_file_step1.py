# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/6/27 16:15
@Author : karsten
@File : generate_station_file_step1.py.py
@Software: PyCharm
============================
"""
import glob
import obspy
from obspy.clients.fdsn import Client as FDSN_Client
client = FDSN_Client("iris")

# 所有台站
stations = glob.glob('../../data/sparta_af_30_eq/PZ/*Z')

starttime = obspy.UTCDateTime("2020-08-09T00:00:00")
endtime = obspy.UTCDateTime("2020-09-09T00:00:00")
# 读取台站信息
for station in stations:
    print(station)
    station_name = station.split('/')[-1]
    net = station_name.split('.')[1]
    sta = station_name.split('.')[2]
    comp = station_name.split('.')[4]
    inv = client.get_stations(network=net, station=sta, location="*",
                              channel=comp,
                              starttime=starttime, endtime=endtime, level="response")
    response_file_path = f"../../data/stations/{net}.{sta}.xml"
    inv.write(response_file_path, format="STATIONXML")