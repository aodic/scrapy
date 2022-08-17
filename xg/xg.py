"""
    :copyright: © 2021 by the JW team.
    :license: MIT, see LICENSE for more details.
"""

#pip3 install openpyxl pandas

import xlwings as xw
import pandas as pd

import os

def ts1():
    #wb = xw.Book.caller()
    #key=xw.sheets[0].range('B3').value
    pass
    

def xg():
    
    from gpPool import gpPool
    s = gpPool()
    s.run()
    df:pd.DataFrame=s.df.sort_values(by=['东方财富行业'])

    sh_Report=xw.sheets["Report"]
    sh_R=xw.sheets["R"]
    sh_L=xw.sheets["L"]
    sh_R.clear_contents()
    sh_L.clear_contents()
    
    sh_R.range('A2').options(index=False).value=df[df['rs']==1]
    sh_L.range('A2').options(index=False).value=df
    
    #保存数据
    #txt1=df[df['ma']==1]['股票代码']
    #txt1.to_csv(f'{os.path.dirname(__file__)}/rs.txt',sep='\t',index=False,header=False)
    
    txt1=df[(df['rs']==1)]['股票代码']
    txt1.to_csv(f'{os.path.dirname(__file__)}/rs.txt',sep='\t',index=False,header=False)
    
    
def main():
    xg()


def ts():
    wb = xw.Book(r'D:\Seafile\J0-Temp\J1\TZ\xg.xlsm')
    sh=wb.sheets['Report']
    a=sh.range(sh.range('H6').value).value
    b='通用设备s' in a
    c=1

