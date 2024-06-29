
#!/bin/bash
echo `pwd`
# 基础参数 ################
EVLA=36.48296
EVLO=-81.09989
EVDP=3.067
Y=2020
D=222
H=12
M=7
S=37
# 转换数据 ################
mseed2sac sparta*.mseed -m sparta0.0.metadata
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
cut t1 -10 60
r *SAC
rtr
rmean
rtr
taper
trans from pol s ../../SAC.PZs to none freq 0.05 0.1 10 150
w over
quit
EOD
cd ..
# 旋转 ###########
rm -rf rotate
mkdir rotate

cd ./data_pre/

file=$(ls *HZ*)
for filename in $file
do
E=$(echo $filename | sed 's/HZ/HE/g')
N=$(echo $filename | sed 's/HZ/HN/g')

R=$(echo $filename | sed 's/HZ.*.SAC/r/g')
T=$(echo $filename | sed 's/HZ.*.SAC/t/g')
Z=$(echo $filename | sed 's/HZ.*.SAC/z/g')

sac << EOD

r $N $E
rotate to gcp
w $R $T

r $filename
w $Z

quit
EOD

done

mv *r *t *z ../rotate

cd ../rotate
