# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/6/28 10:59
@Author : karsten
@File : generate_velocity_model.py
@Software: PyCharm
============================
"""

import numpy as np
import pandas as pd

# 原始速度模型数据
velocity_model = pd.read_csv('../../INPUT/VMODEL/Chapman_Velocity_model',header=None,sep=' ',names=['Depth (km)', 'Speed (km/s)'])
depths = velocity_model['Depth (km)'].values
speeds = velocity_model['Speed (km/s)'].values

# 生成插值的深度范围，每公里一步
new_depths = np.arange(0, 46, 1)  # 从0到45，每公里一步

# 使用numpy进行线性插值
new_speeds = np.interp(new_depths, depths, speeds)

# 将结果转换为DataFrame并保存为CSV文件
interpolated_model = pd.DataFrame({'Depth (km)': new_depths, 'Speed (km/s)': new_speeds})
interpolated_model.to_csv('../../INPUT/VMODEL/Chaoman_interpolated_velocity_model', index=False, sep=' ', header=False)

print(interpolated_model)