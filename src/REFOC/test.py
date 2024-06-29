# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===========================
@Time : 2024/6/27 17:05
@Author : karsten
@File : test.py
@Software: PyCharm
============================
"""
from obspy.core.utcdatetime import UTCDateTime
from obspy import read
import numpy as np
from time import time
import os
import pickle
from sub_sta_vmodel import *
from sub_hashphase import *
import Input_parameters as ip
import pandas as pd
global table
global deptab
global delttab
# fid = open(ip.table_dir+'/table.pickle','rb')
# table = pickle.load(fid)
# fid = open(ip.table_dir+'/deptab.pickle','rb')
# deptab = pickle.load(fid)
# fid = open(ip.table_dir+'/delttab.pickle','rb')
# delttab = pickle.load(fid)

freloc = ip.locfile
fev = ip.evfile
phase_dir = ip.dir_phase
# out_dir = ip.dir_output
# hashphase_dir = ip.dir_hashphase
waveform_dir = ip.wf_dir
fid = open(fev)


for wfline in fid:
    no_wf = 0
    tt1 = time()
    if len(wfline) < 3:
        print('no enough waveform info')
        continue
    lineinfo = wfline.split()
    evid = lineinfo[2]
    dir0 = lineinfo[0]
    dir1 = lineinfo[0] + lineinfo[1]

    pfile = open(phase_dir + '/' + dir0 + '/' + dir1 + '/' +  evid+'/'+evid + '.phase')
    evline = pfile.readline()
    qlat0,qlon0,qdep0,qmag0,qtime0,flag0=get_evinfo(freloc,evid,ftype='reloc')
    print(qlat0,qlon0,qdep0,qmag0,qtime0,flag0)
    qlat, qlon, qdep, qmag, qtime, flag = get_evinfo(evline, evid, ftype='phase')
    for pline in pfile:
        # print(pline)
        net, sta, chan, slat, slon, phase, polar, onset, dist, tt = get_phaseinfo(pline)
        print( net, sta, chan, slat, slon, phase, polar, onset, dist, tt)