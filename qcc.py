import time
import datetime
import json
import re
import requests
import hmac
from hashlib import sha512
from bs4 import BeautifulSoup
import redis


def get_cookies():
    url = 'https://www.qcc.com/'
    ses= requests.Session()
    r=ses.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    tid= soup.find('script', string=re.compile('^window.pid=')).string[-33:-1]
    ck = f'QCCSESSID={ses.cookies.get_dict()["QCCSESSID"]};'
    return ck,tid


#公共变量
RDB=redis.Redis(host='192.168.8.11', port=6379, db=1,decode_responses=True)
CK=get_cookies()
# 临时
# CK=['QCCSESSID=406b6d51d4578bad27da5c9c83;',
#     '0ea19183171f4832ff6c07b5cbfed443']


# 企查查加密
def jm(p, KeyNo):
    """
    参数说明
    api:/api/charts/getequityinvestment
    p:/api/charts/getequityinvestment
    KeyNo:de6d39eb7a4b263d0c7ebdc195940c45
    
    /api/charts/getequityinvestmentpathString{"keyno":"5eb46d79e79bc0d1f18cc9311a0b7d6f"}0ea19183171f4832ff6c07b5cbfed443
    
    """
    
    # 转码
    def hb(k):
        jy = {0: "W", 1: "l", 2: "k", 3: "B", 4: "Q", 5: "g", 6: "f", 7: "i", 8: "i", 9: "r",
                10: "v", 11: "6", 12: "A", 13: "K", 14: "N", 15: "k", 16: "4", 17: "L", 18: "1", 19: "8"}
        k = k.lower()
        rs = ''
        for i in k:
            rs += jy[ord(i) % 20]
        return rs

    p = p.lower()
    _k='{"keyno":"' + KeyNo + '"}'
    _hb=(hb(p)*2).encode()
    m1 = hmac.new(_hb, (p+_k).encode(), sha512).hexdigest()[8:28]
    m2 = hmac.new(_hb, (p + 'pathString' + _k+CK[1]).encode(), sha512).hexdigest()
    
    return m1, m2


# 公司信息查询
def get_company_info(KeyNo):
    rs=None
    r=None #req

    rs=RDB.get(KeyNo)
    if rs:
        return json.loads(rs)
        
    headers = {
        'authority': 'www.qcc.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'cookie': '*',
    }
    url = f'https://www.qcc.com/firm/{KeyNo}.html'
    
    # 结果解析，可考虑单独
    def get_json(rs):
        data=None
        data= json.loads(rs[(rs.find('=') + 1):(rs.rfind(';(function()'))])
        if data.get('company'):
            data=data['company']['companyDetail']
            RDB.set(KeyNo,json.dumps(data),ex=604800)
            return data
        return None

    i = 0  # 循环5次直到成功
    while i < 10:
        i += 1
        r = requests.get(url=url, headers=headers)
        
        if r.status_code!=200:
            print(r.status_code)
            time.sleep(i)
            continue

        #等于200解析
        soup = BeautifulSoup(r.text, 'html.parser')
        rs= soup.find('script', string=re.compile('^window.__INITIAL_STATE__'))
        if rs: #包含在html中
            return get_json(rs.string)
        else: #未包含在html中
            js_path = soup.find('script', src=re.compile('^/web/async-js/'))
            if js_path:
                js_url = 'https://www.qcc.com' + js_path.attrs['src']
                for j in range(2):
                    r = requests.get(url=js_url, headers=headers)
                    rs= r.text
                    if rs:
                        return get_json(rs)
        time.sleep(i)
    return False


# 子公司查询
def get_invest_list(KeyNo):
    data = []
    
    url = 'https://www.qcc.com'
    path = '/api/charts/getEquityInvestment'
    mm = jm(path, KeyNo)
    headers = {
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        'referer': f'{url}/firm/{KeyNo}.html',
        'cookie': CK[0],
        mm[0]: mm[1],
    }

    arg = '{"keyNo":"' + KeyNo + '"}'
    r=None
    i = 0  # 循环5次直到成功
    while i < 5:
        i += 1
        r = requests.post(url=url + path, headers=headers, data=arg)
        if r.status_code==200:
            data = r.json()
            if 'Result' in data:
                return data['Result']['EquityShareDetail']
            return None
        else:
            print(r.status_code)
            time.sleep(i)
            continue
            
    return False


#集团公司清单查询
def get_GC(KeyNo:list,cj=6):
    data = []
    l=[] #keyNoList
    n=0
    
    # 检测缓存
    gc=RDB.get('gc')
    if gc:
        gc=json.loads(gc)
        n=gc['n']
        l=gc['l']
        data=gc['data']
    
    # 添加查询清单
    for i,v in enumerate(KeyNo):
        if v[0] not in l:
            l.append(v[0])
            data.append([v[0],v[1],'存续',1,1,i])
    
    # 缓存
    def rdb_bk():
        rdb_bk={
            'n':n,
            'l':l,
            'data':data
        }
        RDB.set('gc',json.dumps(rdb_bk),ex=604800)
    
    while (True):
        if n >= len(l):
            break
        gs0= data[n]
        _tz=0 # 投资数量
        _cj=gs0[4] # 层级
        _bj=gs0[5] # 集团标记
        if (gs0[3] > 0 and _cj < cj):
            _invest_list=get_invest_list(gs0[0])
            # 失败后缓存退出
            if not _invest_list:
                rdb_bk()
                return False
            # 遍历子公司
            for i in _invest_list:
                if i['ShortStatus']!="注销":
                    _tz+=1
                    _KeyNo=i['KeyNo']
                    if _KeyNo not in l:
                        data.append([i['KeyNo'],i['Name'],i['ShortStatus'],i['DetailCount'],_cj+1,_bj])
                        l.append(_KeyNo)
            gs0[3]=_tz
        n += 1

    rdb_bk()
    return data


def get_GC_info(KeyNo_List:list):
    data=[]
    
    for i in KeyNo_List:
        if i is None:
            data.append([None,None,None,None,None])
            continue
        rs=get_company_info(i)
        if not rs:
            return False

        # zcsj= time.strftime("%Y-%m-%d", time.localtime(rs['StartDate']))
        t=time.localtime(rs['StartDate'])
        zcrq=datetime.date(*t[:3])
        
        # 注册地
        zcd=rs['Area']['City']
        if zcd=='省直辖县级行政区划':
            zcd=rs['Area']['County']
        
        # 委派代表zcd=
        fddbr=''
        fddbr0=rs['Oper']['Name']
        if isinstance(fddbr0,str):
            fddbr0=fddbr0.split('、')
            for i in fddbr0:
                wz0=i.find('公司')
                if wz0!=-1:
                    i=i[:wz0+2]
                fddbr+=(i+'\n')
            fddbr=fddbr[:-1]
        # 注册资本
        zczb=0
        for p in rs['Partners']:
            if p['ShouldCapi'] is None:
                if rs['RegistCapi']:
                    zczb0=rs['RegistCapi']
                    zczb=float(zczb0[:zczb0.find('万')])
                break
            zczb+=float(p['ShouldCapi'])
        
        # 合伙人
        hhr=''
        if len(rs['Partners'])<5:
            for p in rs['Partners']:
                zczb0=p['ShouldCapi']
                if zczb0 is None:
                    zczb0=''
                hhr+=(p['StockName']+'-'+p['StockPercent']+'-'+zczb0+'\n')
        else:
            hhr='更多\n'
        hhr=hhr[:-1]
        
        # 最终结果
        xx=[zcrq,zcd,zczb,fddbr,hhr]
        data.append(xx)
    
    return data


#a=get_company_info('de141fb0592e3b6576bc75a255984564')
#b=1