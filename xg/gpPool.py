"""
    :copyright: © 2021 by the JW team.
    :license: MIT, see LICENSE for more details.
"""
from concurrent.futures import ThreadPoolExecutor
import pandas as pd

from gpModel import jbm,xg


class gpPool():
    def __init__(self):
        """
        gp_list：[[f],[gp_list],[jbm_list]]
        """
        self.gp_list=jbm()
        self.df: pd.DataFrame = None


    #run调用
    def xg(self, gp:list):
        rs=xg(gp[0])
        gp.append(rs)

    
    #启动程序   
    def run(self,x=0):
        if x==0:
            #多线程
            with ThreadPoolExecutor() as pool:
                pool.map(self.xg, self.gp_list[2])
        else:
            #单线程
            [self.xg(i) for i in self.gp_list[2]]
        
        self.get_df()

    #df数据
    def get_df(self):
        
        gp_list=self.gp_list
        gp_list[0].append('rs')
        self.df  = pd.DataFrame(gp_list[1], columns=gp_list[0])
