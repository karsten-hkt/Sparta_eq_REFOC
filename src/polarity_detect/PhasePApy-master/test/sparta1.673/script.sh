
#!/bin/bash
echo `pwd`
# 基础参数 ################
EVLA=36.48075
EVLO=-81.0991
EVDP=3.309
Y=2020
D=224
H=4
M=16
S=47
# 转换数据 ################
mseed2sac sparta*.mseed -m sparta1.673.metadata
mkdir data
mv *SAC data
# 重命名数据 ################
rm -rf data_pre
mkdir data_pre
cd data
sac << EOF
r *.SAC
ch EVLA $EVLA
ch EVLO $EVLO
ch EVDP $EVDP
ch o gmt $Y $D $H $M $S
w over
q
EOF
cp *.SAC ../data_pre/
cd ../data_pre/
taup_setsac -ph P-1,S-3 -evdpkm -model ak135 *.SAC
# 去除仪器响应 ################
sac << EOD
r *SAC
rtr
rmean
rtr
taper
trans from pol s ../../../SAC.PZs to none freq 0.05 0.1 10 150
w over
quit
EOD
