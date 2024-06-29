# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/6/26 17:08
@Author : karsten
@File : picker_DiTing.py
@Software: PyCharm
============================
"""
import os
import glob
import tensorflow as tf
os.environ['CUDA_VISIBLE_DEVICES'] = '2'
import numpy as np
from obspy import UTCDateTime,read,Stream
from keras import backend as K
K.clear_session()
import obspy
import pandas as pd
from obspy.taup import TauPyModel

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

# 导入模型
motion_model = tf.keras.models.load_model('./DiTing-FOCALFLOW-main/models/DiTingMotionJul.hdf5', compile=False)
# 设置记录事件参数的文件
#文件名，震级，发震时间，台站，每个事件对应的信噪比，极性，方位角，p波初至时间，s波初至时间（由taup给定的）
info_record = pd.DataFrame(columns=['event_name', 'event_time', 'event_mag','net', 'sta', 'comp', 'slat','slon','sevla','dist',
									'snr', 'polarity', 'sharpness','ray_azimuth', 'take_off_angle', 'P_time', 'S_time'])
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
		comp = tr.stats.channel
		net = tr.stats.network
		slat = tr.stats.sac.stla
		slon = tr.stats.sac.stlo
		sevla = tr.stats.sac.stel
		dist = tr.stats.sac.dist
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
		polarity = 'x'
		sharpness = 'x'
		if snr >= 2:
			# 计算极性
			# 数据预处理
			tr.detrend('demean')
			try:
				tr.detrend(type='linear')
			except:
				tr.detrend(type='constant')
			tr = tr.taper(0.001)
			tr_p = tr.copy()
			tr_p.trim(tr.stats.starttime + tr.stats.sac.t1 - 5 - 0.64, tr.stats.starttime + tr.stats.sac.t1 - 5 + 0.64)
			Hz = int(tr_p.stats.sampling_rate)
			motion_input = np.zeros([1, 128, 2])
			motion_input[0, :, 0] = tr.data[0:128]
			if np.max(motion_input[0, :, 0]) == 0:
				pass
			else:
				motion_input[0, :, 0] -= np.mean(motion_input[0, :, 0])
				norm_factor = np.std(motion_input[0, :, 0])

				if norm_factor == 0:
					pass
				else:
					motion_input[0, :, 0] /= norm_factor
					diff_data = np.diff(motion_input[0, 64:, 0])
					diff_sign_data = np.sign(diff_data)
					motion_input[0, 65:, 1] = diff_sign_data[:]
			# 模型预测
			pred_res = motion_model.predict(motion_input)
			pred_fmp = (pred_res['T0D0'] + pred_res['T0D1'] + pred_res['T0D2'] + pred_res['T0D3']) / 4
			pred_cla = (pred_res['T1D0'] + pred_res['T1D1'] + pred_res['T1D2'] + pred_res['T1D3']) / 4
			if np.argmax(pred_fmp[0, :]) == 1:
				polarity = 'D'
				if np.argmax(pred_cla[0, :]) == 0:
					sharpness = 'I'
				elif np.argmax(pred_cla[0, :]) == 1:
					sharpness = 'E'
				else:
					sharpness = 'x'
			elif np.argmax(pred_fmp[0, :]) == 0:
				polarity = 'U'
				if np.argmax(pred_cla[0, :]) == 0:
					sharpness = 'I'
				elif np.argmax(pred_cla[0, :]) == 1:
					sharpness = 'E'
				else:
					sharpness = 'x'
			else:
				polarity = 'x'
				if np.argmax(pred_cla[0, :]) == 0:
					sharpness = 'I'
				elif np.argmax(pred_cla[0, :]) == 1:
					sharpness = 'E'
				else:
					sharpness = 'x'
		# print(polarity, sharpness)
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
			'net': [net],
			'comp': [comp],
			'slat': [slat],
			'slon': [slon],
			'sevla': [sevla],
			'dist': [dist],
			'snr': [snr],
			'polarity': [polarity],
			'sharpness': [sharpness],
			'ray_azimuth': [ray_azimuth],
			'take_off_angle': [take_off_angle],
			'P_time': [P_time],
			'S_time': [S_time]
		})
		info_record = pd.concat([info_record, new_record], ignore_index=True)
# 保存到文件
info_record.to_csv('../../output/polarity_info_based_on_DiTing/picker_info.csv', index=False)