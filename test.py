# import pymysql
#
#
# def connect_mysql():
#     connmysql = pymysql.connect(host='116.125.18.51', port=23306, user='coin', password='eler3155', db='coin',
#                                 charset='utf8')
#
#
# def load_chart_data(fpath):
#     # chart_data = pd.read_csv(fpath, thousands=',', header=None)
#
#     chart_data = pd.read_sql("select * from MAIMAIDATA", connmysql)
#     chart_data.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'inst', 'frgn']
#     chart_data['inst'] = pd.to_numeric(chart_data['inst'].str.replace(',', ''), errors='coerce')
#     chart_data['frgn'] = pd.to_numeric(chart_data['frgn'].str.replace(',', ''), errors='coerce')
#     return chart_data

import tensorflow as tf
hello = tf.constant('Hello, Tensor')
sess = tf.Session()
print(sess.run(hello));
model = multi_gpu_mode(model, gpus=8)
print(model.summary());


