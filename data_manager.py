import pandas as pd
import numpy as np
import os
# fpath = os.path.expanduser('/aicsvc/app/autocoin/data/chart_data/005930.csv')
import pymysql
import configparser

config = configparser.ConfigParser()
config.read('/aicsvc/app/config.ini')
myip = config['MYSQL']['myip']
myport = config['MYSQL']['myport']
myid = config['MYSQL']['myid']
mypw = config['MYSQL']['mypw']

connmysql = pymysql.connect(myip, myid, mypw, db='coin', charset='utf8', port=23306)# %myport
curs = connmysql.cursor(pymysql.cursors.DictCursor)
# listsql = "select `NAME` from INFO"
sql = " select date, open, high, low, close, volume from coin.MAIMAIDATA where NAME='%s' order by NO desc "  %("BTC")
# curs.execute(sql)
# curs.execute(listsql)
# rows = curs.fetchall()
# print(rows);
# connmysql.commit()
# connmysql.close()
    # chart_data = pd.read_csv(fpath, thousands=',', header=None)
    # chart_data = pd.read_sql(sql,connmysql)
    # chart_data = pd.DataFrame(rows)


def load_chart_data(sql):
    chart_data = pd.read_sql(sql, connmysql)
    # chart_data = pd.read_csv(fpath, thousands=',', header=None)
    # chart_data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    # print(chart_data);
    return chart_data
# print(load_chart_data(sql));

def preprocess(chart_data):
    prep_data = chart_data
    windows = [5, 10, 20, 60, 120]
    for window in windows:
        prep_data['close_ma{}'.format(window)] = prep_data['close'].rolling(window).mean()
        prep_data['volume_ma{}'.format(window)] = (
            prep_data['volume'].rolling(window).mean())
    return prep_data


def build_training_data(prep_data):
    training_data = prep_data

    training_data['open_lastclose_ratio'] = np.zeros(len(training_data))
    training_data.loc[1:, 'open_lastclose_ratio'] = \
        (training_data['open'][1:].values - training_data['close'][:-1].values) / \
        training_data['close'][:-1].values
    training_data['high_close_ratio'] = \
        (training_data['high'].values - training_data['close'].values) / \
        training_data['close'].values
    training_data['low_close_ratio'] = \
        (training_data['low'].values - training_data['close'].values) / \
        training_data['close'].values
    training_data['close_lastclose_ratio'] = np.zeros(len(training_data))
    training_data.loc[1:, 'close_lastclose_ratio'] = \
        (training_data['close'][1:].values - training_data['close'][:-1].values) / \
        training_data['close'][:-1].values
    training_data['volume_lastvolume_ratio'] = np.zeros(len(training_data))
    training_data.loc[1:, 'volume_lastvolume_ratio'] = \
        (training_data['volume'][1:].values - training_data['volume'][:-1].values) / \
        training_data['volume'][:-1]\
            .replace(to_replace=0, method='ffill') \
            .replace(to_replace=0, method='bfill').values

    windows = [5, 10, 20, 60, 120]
    for window in windows:
        training_data['close_ma%d_ratio' % window] = \
            (training_data['close'] - training_data['close_ma%d' % window]) / \
            training_data['close_ma%d' % window]
        training_data['volume_ma%d_ratio' % window] = \
            (training_data['volume'] - training_data['volume_ma%d' % window]) / \
            training_data['volume_ma%d' % window]

    return training_data


# chart_data = pd.read_csv(fpath, encoding='CP949', thousands=',', engine='python')
# data = load_chart_data()
# print(data);
