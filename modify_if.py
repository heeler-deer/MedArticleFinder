'''
# @author: heeler-deer
# @date: 2023-09-21
# @file: medicine.py
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


file_handler = logging.FileHandler('modify_if.log', mode='w')
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)






def get_IF_from_name(name):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0"
    }
    name.replace(" ", "+")
    address = (
        "http://sci.justscience.cn/list?q="
        + str(name)
        + "&sci=1"
        + "&research_area=&If_range_min=&If_range_max=&jcr_quartile=0&oa=2&Self_cites_ratio_min=&Self_cites_ratio_max=&mainclass=0&subclass=0&pub_country=&not_pub_country=&sci_type=2&pub_frequency=7&adv=1"
    )
    logger.info(address)
    f = requests.get(address, headers=headers, timeout=(3, 7))

    parsed_html = html.fromstring(f.content)

    tr_elements = parsed_html.xpath(
        "/html/body/div[1]/div[1]/div[2]/div[2]/table/tbody/tr"
    )

    for tr in tr_elements:
        logger.info("::::::::::::::::::::::::::")
        
        row_data = tr.xpath("td[1]/a/text()")
        row_data2 = tr.xpath("td[2]/text()")
        try:
            row_data = str(row_data[0])
            row_data2 = str(row_data2[0])
        except Exception as e:
            return "N"

        logger.info(row_data.strip().upper())

        logger.info(name.strip().upper())
        try:
            time.sleep(1)
            logger.info(tr.xpath("td[7]/text()")[0])

            return tr.xpath("td[7]/text()")[0]
        except Exception as e:
            logger.error("**********Error**********")
            return "N"
        
df = pd.read_excel('article_info 664.xlsx')
for  index, row in df.iterrows():
    journal=row['Journal']
    
    logger.info(journal)
    result=get_IF_from_name(journal)
    logger.info(result)
    df.at[index, 'IF'] = result
    
df.to_excel('article_info 664.xlsx', index=False)