# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/6/26 09:40
@Author : karsten
@File : picker_PhasePApy.py.py
@Software: PyCharm
============================
"""
import obspy
import pandas as pd
import numpy as np
import glob
from obspy.taup import TauPyModel
import sys
sys.path.append("./PhasePApy-master")
from phasepapy.phasepicker import aicdpicker

def snr_cal(noise, P_signal, S_signal):
	"""
	计算信噪比
	:param noise: 噪声
	:param signal: 信号
	:return: 信噪比
	"""
	# 转换为numpy
	noise = np.array(noise.data)
	P_signal = np.array(P_signal.data)
	S_signal = np.array(S_signal.data)
	# 计算rms
	noise_rms = np.sqrt(np.mean(noise ** 2))
	P_signal_rms = np.sqrt(np.mean(P_signal ** 2))
	S_signal_rms = np.sqrt(np.mean(S_signal ** 2))
	# 计算信噪比
	snr = 10*np.log10(0.5*(P_signal_rms+S_signal_rms) / noise_rms)
	return snr

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

# 所有的事件文件夹
event_folder = '../../data/sparta_af_30_eq/sac_data'
# 读取所有的文件
events = glob.glob(event_folder + '/*')
# 按照名称排序
events.sort()
#
# 设置记录事件参数的文件
#文件名，震级，发震时间，台站，每个事件对应的信噪比，极性，方位角，p波初至时间，s波初至时间（由taup给定的）
info_record = pd.DataFrame(columns=['event_name', 'event_time', 'event_mag', 'sta', 'snr', 'polarity', 'ray_azimuth', 'take_off_angle', 'P_time', 'S_time'])
for i,event in enumerate(events):
	# 读取内部对应的sac文件
	sac_files = obspy.read(event + '/rotate/*.z')
	event_name = event.split('/')[-1]
	event_time = data['formatted_datetime'][i]
	event_mag = data['mag'][i]
	for sac_file in sac_files:
		# 读取文件
		tr = sac_file
		sta = tr.stats.station
		P_time = tr.stats.starttime + tr.stats.sac.t1 - 5
		S_time = tr.stats.starttime + tr.stats.sac.t3 - 5
		# 滤波
		tr.filter('bandpass', freqmin=1, freqmax=10, corners=2, zerophase=True)
		# 截取P波到达前2.5–0.5 s作为noise windows
		tr_noise = tr.copy()
		tr_noise.trim(tr_noise.stats.starttime + tr_noise.stats.sac.t1 - 5-2.5, tr_noise.stats.starttime +tr_noise.stats.sac.t1 - 5- 0.5)
		# 截取P波，S波时窗
		tr_P = tr.copy()
		tr_P.trim(tr_noise.stats.starttime + tr_P.stats.sac.t1- 5-0.5, tr_noise.stats.starttime +tr_P.stats.sac.t1 - 5+ 1.5)
		# 绘制看看
		tr_S = tr.copy()
		tr_S.trim(tr_noise.stats.starttime + tr_S.stats.sac.t3-5-0.5, tr_noise.stats.starttime +tr_S.stats.sac.t3 - 5+ 1.5)
		# 计算信噪比
		snr = snr_cal(tr_noise, tr_P, tr_S)
		polarity = []
		if snr >= 2:
			# 计算极性
			chenPicker = aicdpicker.AICDPicker(t_ma = 3, nsigma = 8, t_up = 0.78, nr_len = 2, nr_coeff = 2, pol_len = 10, pol_coeff = 10, uncert_coeff = 3)
			_, _, polarity, _, _ = chenPicker.picks(tr)
		ray_azimuth = tr.stats.sac.az
		# 计算入射角
		model = TauPyModel(model='iasp91')
		try:
			arrivals = model.get_ray_paths(source_depth_in_km=tr.stats.sac.evdp, distance_in_degree=tr.stats.sac.gcarc,
										   phase_list=["P", "S"])
			take_off_angle = arrivals[0].takeoff_angle if arrivals else None
		except Exception as e:
			take_off_angle = None
			print(f"Error computing takeoff angle: {e}")
		# 记录到info_record
		new_record = pd.DataFrame({
			'event_name': [event_name],
			'event_time': [event_time],
			'event_mag': [event_mag],
			'sta': [sta],
			'snr': [snr],
			'polarity': [polarity],
			'ray_azimuth': [ray_azimuth],
			'take_off_angle': [take_off_angle],
			'P_time': [P_time],
			'S_time': [S_time]
		})
		info_record = pd.concat([info_record, new_record], ignore_index=True)
	if i==5:
		break
# 保存到文件
info_record.to_csv('../../output/polarity_info_based_on_PhasePApy-master/picker_info.csv', index=False)