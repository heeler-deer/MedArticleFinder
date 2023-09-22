'''
# @author: heeler-deer
# @date: 2023-09-21
# @file: medicine.py
'''

from scihub import SciHub
import pandas as pd
import glob
import requests
import time
from bs4 import BeautifulSoup
from pygtrans import Translate
import time
import json
from lxml import html
from scholarly import scholarly
import re
import random
import logging
import colorlog
import os

root_logger = logging.getLogger()
if root_logger.handlers:
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
        

logger = colorlog.getLogger()
logger.setLevel(logging.DEBUG)


console_handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)
console_handler.setFormatter(formatter)


file_handler = logging.FileHandler('modify_cohindex.log', mode='w')
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)






directory = "./paper/"


filelist = os.listdir(directory)


file_names = []


for filename in filelist:
    
    name, ext = os.path.splitext(filename)
    
    file_names.append(name)





logger.info(file_names)


df = pd.read_excel('article_info 664.xlsx')
cnt=0
cnt2=0
for  index, row in df.iterrows():
    
    title=row['Title']
    
    logger.info(title)
    
    if (title in file_names):
        result="Y"
        cnt=cnt+1
    else:
        result=""
        cnt2=cnt2+1
    logger.info(result)
    
    df.at[index, 'co-hindex'] = result

logger.info(cnt)
logger.info(cnt2)
df.to_excel('article_info 664.xlsx', index=False)