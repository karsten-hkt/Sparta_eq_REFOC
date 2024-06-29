# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/6/27 18:37
@Author : karsten
@File : generate_phase_file.py.py
@Software: PyCharm
============================
"""
import datetime
import pandas as pd
import os

# 读取pick_info
pick_info = pd.read_csv('../../output/polarity_info_based_on_DiTing/picker_info.csv')
event_info = pd.read_csv('../../INPUT/evlist_ex', sep=' ', header=None,names=['year', 'month', 'day_interval', 'lat', 'lon', 'depth', 'mag', 'file_locate'])
reloc_info = pd.read_csv('../../INPUT/sparta_relocation.txt', sep=' ', header=None, names=['year', 'month', 'day', 'hour', 'minute', 'second', 'day_interval', 'lat', 'lon', 'depth', 'mag', 'ex', 'ey', 'ez', 'et', 'velocity_model'])
# 保存位置
save_dir = '../../INPUT/PHASE'

for i in range(len(event_info)):
	event_dir = event_info.loc[i,'file_locate']
	# 创建文件夹
	if not os.path.exists(f'{save_dir}/{event_dir}'):
		os.makedirs(f'{save_dir}/{event_dir}')

	# 读取event_info的每一行
	# 第一行保持不变，用pandas读取
	event = event_info.iloc[i]
	reloc = reloc_info.iloc[i]
	# 读取该事件对应的pick_info
	day_interval = event.loc['day_interval']
	pick_info_event = pick_info[pick_info['event_name'] == f'sparta{day_interval}']
	# 重排索引
	pick_info_event = pick_info_event.reset_index(drop=True)
	picker_line = pd.DataFrame(columns=['net','sta','comp','code','slat','slon','sevla', 'phase', 'polar','onset','weight', 'dist', 'tt'])
	# 读取pick_info的每一行并保存到picker_line
	for j in range(len(pick_info_event)):
		picker_line.loc[j,'net'] = pick_info_event.loc[j,'net']
		picker_line.loc[j,'sta'] = pick_info_event.loc[j,'sta']
		picker_line.loc[j,'comp'] = pick_info_event.loc[j,'comp']
		picker_line.loc[j,'code'] = '--'
		picker_line.loc[j,'slat'] = pick_info_event.loc[j,'slat']
		picker_line.loc[j,'slon'] = pick_info_event.loc[j,'slon']
		picker_line.loc[j,'sevla'] = pick_info_event.loc[j,'sevla']
		picker_line.loc[j,'phase'] = 'P'
		polar = pick_info_event.loc[j,'polarity']
		if polar == 'U':
			picker_line.loc[j,'polar'] = 'c'
		elif polar == 'D':
			picker_line.loc[j,'polar'] = 'd'
		else:
			picker_line.loc[j,'polar'] = '.'
		picker_line.loc[j,'onset'] = pick_info_event.loc[j,'sharpness']
		picker_line.loc[j,'weight'] = 1
		picker_line.loc[j,'dist'] = pick_info_event.loc[j,'dist']
		P_time = pick_info_event.loc[j,'P_time']
		start_time = pick_info_event.loc[j,'event_time']
		# 计算tt，用datetime
		start_time = datetime.datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
		P_time = datetime.datetime.strptime(P_time, '%Y-%m-%dT%H:%M:%S.%fZ')
		tt = (P_time - start_time).total_seconds()
		picker_line.loc[j,'tt'] = tt

	# 生成文件
	with open(f'{save_dir}/{event_dir}/{day_interval}.phase', 'w') as f:
		# 写入事件信息['year', 'month', 'day', 'hour', 'minute', 'second', 'day_interval', 'lat', 'lon', 'depth', 'mag', 'ex', 'ey', 'ez', 'et', 'velocity_model']
		f.write(f'{reloc.year} {reloc.month} {reloc.day} {reloc.hour} {reloc.minute} {reloc.second} {reloc.day_interval} {reloc.lat:.5f}'
				f' {reloc.lon:.5f} {reloc.depth:.3f} {reloc.mag:.2f} {reloc.ex:.3f} {reloc.ey:.3f} {reloc.ez:.3f} {reloc.et:.3f} {reloc.velocity_model}\n')
		# 写入每一行pick信息
		for index, row in picker_line.iterrows():
			f.write(f"{row['net']}  {row['sta']}  {row['comp']} {row['code']}  {row['slat']:.4f}  {row['slon']:.4f}  "
					f"{row['sevla']:.1f} {row['phase']} {row['polar']} e  {row['weight']}  {row['dist']:.2f}  {row['tt']:.3f}\n")




