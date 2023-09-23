'''
# @author: heeler-deer
# @date: 2023-09-21
# @file: medicine.py
'''


'''
download article by their sci-hub urls
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


from scihub import SciHub

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


file_handler = logging.FileHandler('download_article.log', mode='w')
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)

def download_paper(url,title):
    sh = SciHub()
    logger.info("**********Getting paper by scihub url**********")
    # exactly the same thing as fetch except downloads the articles to disk
    # if no path given, a unique name will be used as the file name
    try:
        logger.info(title)
        logger.info(url)
        result = sh.download(url, path='./paper/'+title+".pdf")
        logger.info("***************************")
        logger.info("**********Success**********")
        logger.info("***************************")
        return "Y"
    except Exception as e:
        logger.error("**********Can't find url**********")
        return ""









df = pd.read_excel('article_info 664.xlsx')
for  index, row in df.iterrows():
    url=row['Document_url']
    title=row['Title']
    logger.info(url)
    logger.info(title)
    result=download_paper(url,title)
    time.sleep(3)
    logger.info(result)
    df.at[index, 'co-hindex'] = result
    
df.to_excel('article_info 664.xlsx', index=False)

    