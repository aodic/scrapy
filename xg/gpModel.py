"""
    :copyright: © 2021 by the JW team.
    :license: MIT, see LICENSE for more details.
"""
from heapq import nlargest
from optparse import Values
from platform import mac_ver
from time import sleep
from xmlrpc.client import Boolean
import pandas as pd
from gpData import get_list2,get_rk2


#基本面选股
def jbm():
    gp_list=get_list2()
    jbm_list=[]
    
    if gp_list is None:
        return None
    
    #基本面选股条件
    for i in gp_list[1]:
        #排除条件
        if (#股票代码
            i[0][0] == '8' or
            i[0][0] == '4' or
            #股票名称
            i[1][0] == 'S' or
            i[1][0:2] == '*S' or
            i[1][0] == '退' or
            i[1][-1] == '退' or
            #股价3-100
            i[3] < 3 or
            i[3] > 50 or
            #流通市值10-500
            i[6] < 10 or
            i[6] > 300
            #市盈率
            # i[9] > 200 or
            # i[9] < 0 or
        ):
            continue
        else:
            jbm_list.append(i)
    gp_list.append(jbm_list)
    return gp_list


#日K线数据
def __rk__(code=None,N1=0) -> pd.DataFrame:
    """
    数据初始化，增加均线，排序，清洗等
    最终返回数据日期为降序
    """
    
    if code is None:
        return None
    
    N = 250  # 1年初始数据
    rk = get_rk2(code, days=N)

    df = pd.DataFrame(rk[1], columns=rk[0])
    df.set_index('Date', inplace=True)
    
    # 返回N天前的数据
    if N1>0:
        df=df.iloc[:-N1]

    # 添加均线，日期需升序排列
    df['ma5'] = round(df['C'].rolling(window=5, min_periods=1).mean(), 2)
    df['ma13'] = round(df['C'].rolling(window=13, min_periods=1).mean(), 2)
    df['ma21'] = round(df['C'].rolling(window=21, min_periods=1).mean(), 2)
    df['ma30'] = round(df['C'].rolling(window=30, min_periods=1).mean(), 2)
    df['ma60'] = round(df['C'].rolling(window=60, min_periods=1).mean(), 2)
    # df['ma120'] = round(df['C'].rolling(window=120, min_periods=1).mean(), 2)
    # df['ma250'] = round(df['C'].rolling(window=250, min_periods=1).mean(), 2)
    
    #返回降序日期
    df.sort_index(axis=0,ascending=False,inplace=True)
    
    return df


#调用具体条件选股
def xg(code):
    
    df=__rk__(code)
    if df is None:
        return None
    
    N=90 # 日K数据范围
    if len(df) < N:
        return 0
    
    #均线
    if not __ma__(df):
        return -1
    
     #横盘
    if not __hp__(df):
        return -2

    return 1


#均线多头策略
def __ma__(df:pd.DataFrame)->Boolean:

    np =df.iloc[0]
    ma30=df.head(10)['ma30']
    ma60=df.head(10)['ma60']

    if (np['C']>=np['ma21'] and
        #np['C']/np['ma13']<1.3 and
        np['ma5'] >=np['ma21'] >=np['ma30'] and
        ma30[0]/ma30[9]>=1.02
        #ma60[0]/ma60[4]>=0.98
    ):
        return True
    
    return False

#df横盘整理
def __v__(df:pd.DataFrame)->Boolean:
    
    v=df.head(60)['V']
    
    v21=v.iloc[:21].mean()
    v60=v.mean()
    
    if v21>v60:
        return True

    return False



#df横盘整理
def __hp__(df:pd.DataFrame)->Boolean:
    
    v=df.head(30)['ma5']
    
    n0=1
    zdz=v.iloc[0]
    zxz=v.iloc[0]
    
    for i in v.iloc[1:]:
        if i>zdz:
            zdz=i
        elif i<zxz:
            zxz=i
        
        if zdz/zxz>1.02:
            break
        n0+=1
        if n0>5:
            return True
    
    return False




