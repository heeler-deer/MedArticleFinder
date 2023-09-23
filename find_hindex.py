'''
# @author: heeler-deer
# @date: 2023-09-21
# @file: medicine.py
'''


'''
find h-index by name of the author
NOTE!!!!!!
While there may be duplicate names, 
it's important to note that the code cannot guarantee 
the absolute reliability of the h-index.
'''


import json
import logging
import random
import time
import glob
import re

import requests
from bs4 import BeautifulSoup
from lxml import html
import colorlog
import pandas as pd
from pygtrans import Translate
from scholarly import scholarly




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


file_handler = logging.FileHandler('find_hindex.log', mode='w')
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)

article_info_list = []



def get_hindex_by_author(name):
    name=name.split(",")[0]
    
    logger.info("**********Getting hindex by author**********")
    logger.info(name)
    try:
        search_query = scholarly.search_author(name)

        author = next(search_query)

        scholarly.pprint(scholarly.fill(author, sections=["indices"]))
        hindex = scholarly.fill(author, sections=["indices"])["hindex"]
        if hindex == None:
            logger.error("**********No hindex as hindex==None**********")
            hindex = "N"
        logger.info(hindex)
        random_integer = random.randint(2, 4)
        time.sleep(random_integer)
        return hindex
    except Exception as e:
        logger.error("**********No hindex as got exception**********")
        hindex = "N"
        return hindex






df = pd.read_excel('article_info 664.xlsx')


df['hindex'] = df['Authors'].apply(get_hindex_by_author)


df.to_excel('article_info 664.xlsx', index=False)