import pandas as pd
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

#读取数据
data_locate = '../../data/sparta_eq_catalog/supplementary_data1_relocated_catalog_sparta.txt'
df = pd.read_csv(data_locate, sep='\s+', header=None, names=["ID", "YYYY", "MM", "dd", "hh", "mm", "ss.sss", "lat", "lon", "depth", "mag", "ex", "ey", "ez", "et", "rms"])
# 转换时间格式
df['datetime'] = pd.to_datetime(df['YYYY'].astype(str) + '-' + df['MM'].astype(str) + '-' +
								df['dd'].astype(str) + ' ' + df['hh'].astype(str) + ':' + df['mm'].astype(str) +
								':' + df['ss.sss'].astype(str))
# 按要求的格式输出时间
df['formatted_datetime'] = df['datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S')
# 提取需要的列
data = df[['formatted_datetime', 'lat', 'lon', 'depth', 'mag']]
#计算时间间隔
start_time = '2020-08-09T12:07:37'
datetimeFormat = '%Y-%m-%dT%H:%M:%S'
diff_days = time_delta(data.iloc[:,0], start_time, datetimeFormat)
#将时间间隔插入data中
data.insert(0,'Day_interval',diff_days)
#筛选出震后的数据，深度大于0的
data = data[data['Day_interval']>=0]
data = data[data['depth']>0]
# data = data[data['mag']!='-']
#对时间间隔进行升序
data = data.sort_values(by=['Day_interval'],ascending=True)
data = data.reset_index(drop=True)
#保存成新的文件

data.to_csv('../../data/sparta_eq_catalog/data_processing.csv',index=0)
