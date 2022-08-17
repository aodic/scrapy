"""
    :copyright: © 2021 by the JW team.
    :license: MIT, see LICENSE for more details.
"""

#pip3 install openpyxl pandas

import time

from gpPool import gpPool

def run():
    start = time.time()
    s = gpPool()
    s.run()

    
    a=1

if __name__ == '__main__':
    run()