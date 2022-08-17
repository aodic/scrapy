import json
import requests
from datetime import date

#到处函数为get_list2,get_rk2

def get_list(l=10000):
    # 参数pz=10，股票总数
    #   f12,     f14,      f26,    f2,   f3,   f20,    f21,    f8,      f6,      f9,     f23,    f100,     f102,f103
    # 股票代码，股票名称，上市日期，最新价，涨幅，总市值，流通市值，换手率，成交金额，市盈率，市净率，东方财富行业，地区，概念
    url = 'http://8.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112406787329742802122_1638531523132'
    url += '&pn=1&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3'
    url += '&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&pz=' + str(l)
    url += '&fields=f12,f14,f26,f2,f3,f20,f21,f8,f6,f9,f23,f100,f102,f103&_=1638531523133'

    r = requests.get(url=url)
    t = r.text[r.text.find('(') + 1:-2]
    t = json.loads(t)['data']['diff']

    return t


def get_date(x):
    x = str(x)
    if x == '-':
        return None
    return date(int(x[0:4]), int(x[4:6]), int(x[6:8]))


def get_int(x):
    if x == '-':
        return 0
    return round(x / 100000000, 2)


def get_zero(x):
    if x == '-':
        return 0
    return x


def get_list2(l=10000):
    gplist = get_list(l)
    data = []

    for i in gplist:
        data.append([
            i['f12'],
            i['f14'],
            get_date(i['f26']),
            get_zero(i['f2']),
            get_zero(i['f3']),
            get_int(i['f20']),
            get_int(i['f21']),
            get_zero(i['f8']),
            get_int(i['f6']),
            get_zero(i['f9']),
            get_zero(i['f23']),
            i['f100'],
            i['f102'],
            i['f103']
        ])
    columns = [
        '股票代码',  # 0-12
        '股票名称',  # 1-14
        '上市日期',  # 2-26
        '最新价',   # 3-2
        '涨幅',     # 4-3
        '总市值',   # 5-20
        '流通市值',  # 6-21
        '换手率',   # 7-8
        '成交金额',  # 8-6
        '市盈率',   # 9-9
        '市净率',   # 10-23
        '东方财富行业',  # 11-100
        '地区',     # 12-102
        '概念'      # 13-103
    ]
    return [columns, data]


def get_rk(code, days=20000, fqt=1):
    SECID = {
        '0': '0.',
        '3': '0.',
        '4': '0.',
        '8': '0.',
        '6': '1.',
    }

    # "2021-12-03,6.54,6.44,6.60,6.41,66008,42681310.00,2.90,-1.68,-0.11,4.30"
    # 交易日期，开盘价，收盘价，最高价，最低价，成交量，成交金额，振幅，涨跌幅，涨跌额，换手率
    # fqt=0-除权，1-前复权，2-后复权。
    url = 'http://58.push2his.eastmoney.com/api/qt/stock/kline/get?cb=jQuery112406240810966471757_1638549505318'
    url += '&ut=fa5fd1943c7b386f172d6893dbfba10b&klt=101&fqt=' + str(fqt)
    url += '&end=20500101&_=1638549505368&lmt=' + str(days)
    url += '&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61'
    url += '&secid=' + SECID[code[:1]] + code

    rs = requests.get(url).text
    t = rs[rs.find('(') + 1:-2]
    t = json.loads(t)['data']['klines']

    return code, t


def get_rk2(code, days=20000, fqt=1):
    data = []
    columns = ['Date', 'O', 'C', 'H', 'L', 'V', 'Amount', 'Amplitude', 'CP', 'CA', 'TR', ]
    rs = get_rk(code=code, days=days, fqt=fqt)
    for i in rs[1]:
        t = i.split(',')
        data.append([
            get_date2(t[0]),
            float(t[1]),
            float(t[2]),
            float(t[3]),
            float(t[4]),
            float(t[5]),
            float(t[6]),
            float(t[7]),
            float(t[8]),
            float(t[9]),
            float(t[10])
        ])
    return columns, data


def get_date2(x):
    x = x.split('-')
    return date(int(x[0]), int(x[1]), int(x[2]))
