'''
# @author: heeler-deer
# @date: 2023-09-21
# @file: medicine.py
'''


'''
find articles by keywords and convert them to csv files
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


file_handler = logging.FileHandler('medicine.log', mode='w')
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)




class ArticleInfo:
    def __init__(
        self,
        pmid,
        year,
        title,
        authors,
        journal,
        rcr,
        np,
        citation,
        fcr,
        IF,
        abstract,
        keywords,
        source_url,
        matching_keywords,
        category,
        hindex,
        doi,
        document_url
    ):

        self.pmid = pmid
        self.year = year
        self.title = title
        self.authors = authors
        self.journal = journal
        self.rcr = rcr
        self.np = np
        self.citation = citation
        self.fcr = fcr
        self.IF = IF
        self.abstract = abstract
        self.keywords = keywords
        self.source_url = source_url
        self.doi = doi
        self.document_url = document_url
        self.category = category
        self.matching_keywords = matching_keywords
        self.hindex = hindex
        self.cohindex = "N"


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
    f = requests.get(address, headers=headers, timeout=(10, 50))

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
        if (
            row_data.strip().upper() == name.strip().upper()
            or row_data2.strip().upper() == name.strip().upper()
        ):
            time.sleep(0)
            logger.info(tr.xpath("td[7]/text()")[0])

            return tr.xpath("td[7]/text()")[0]


def get_article_by_keyword(key, key2):
    pmid_result_list = []

    key_year = [2013]
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&amp;term=shampoo+AND+zinc+AND+
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=science%5bjournal%5d+AND+breast+cancer+AND+2008
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0"
    }
    logger.info("**********Getting pmid of article**********")
    for key3 in key_year:
        address = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=3000&term=%5bjournal%5d+AND+"
        # address = address + key + "+" + key2 + "+AND+" + str(key3)
        address = address + key  + "+AND+" + \
            "(%221800/01/01%22[Date%20-%20Publication]%20:%20%222023/12/31%22[Date%20-%20Publication])"
        logger.info(address)
        f = requests.get(address, headers=headers, timeout=(10, 50))
        soup = BeautifulSoup(f.text, features="xml")

        count = soup.find("Count").text
        logger.info("|  Count  |  key1  |  key2  |  key3  |")
        logger.info(
            "|  "
            + str(count)
            + "  |  "
            + str(key)
            + "  |  "
            + str("")
            + "  |  "
            + str("")
            + "  |"
        )
        if count == "0":
            logger.info(
                "Find no articles about:  "
                + str(key)
                + "  "
                + str(key2)
                + "  "
                + str(key3)
            )
            return ["error"]

        id_list = soup.find_all("Id")
        for id_element in id_list:
            logger.info("Id:" + id_element.text)

            pmid_result_list.append(id_element.text)
        logger.info("%s", pmid_result_list)

        time.sleep(0)

    return pmid_result_list


def get_details_by_pmid(pmid_list, matching_keywords, category):
    article_info_list=[]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0"
    }
    if pmid_list[0] == "error":

        return
    # https://icite.od.nih.gov/api/pubs?pmids=28968381,28324054,23843509&fl=pmid,year,title,apt,relative_citation_ratio,cited_by_clin
    logger.info("**********Getting details by pmid**********")
    address = (
        "https://icite.od.nih.gov/api/pubs?pmids="
        + ",".join(pmid_list)
        + "&fl=pmid,year,title,authors,journal,relative_citation_ratio,nih_percentile,citation_count,field_citation_rate,doi"
    )
    logger.info(address)
    f = requests.get(address, headers=headers, timeout=(10, 50))
    response = f.text
    soup = json.loads(response)

    for item in soup["data"]:
        logger.info("PMID:" + str(item["pmid"]))

        logger.info("Year:" + str(item["year"]))
        title= re.sub(r"<.*?>", "", item["title"])
        title=re.sub(r"[.*?]", "", title)
        logger.info("Title:" + title)
        logger.info("Authors:" + item["authors"])
        logger.info("Journal:" + item["journal"])
        logger.info("Relative Citation Ratio:" +
                    str(item["relative_citation_ratio"]))
        logger.info("NIH Percentile:" + str(item["nih_percentile"]))
        logger.info("Citation Count:" + str(item["citation_count"]))
        logger.info("Field Citation Rate:" + str(item["field_citation_rate"]))
        logger.info("DOI:"+str(item["doi"]))
        # build IF,source_url,abstract,keywords,document_url

        IF = get_IF_from_name(item["journal"])
        if IF == None:
            IF = "N"
        logger.info("Impact Factor:" + IF)
        source_url = "https://pubmed.ncbi.nlm.nih.gov/" + \
            str(item["pmid"]) + "/"

        abstract, keywords = get_abstract_keywords_by_pmid(item["pmid"])
        #TODO  key is list , but now it is a str
        logger.info(matching_keywords)
        category = category
        # if (
        #     key == "dandruff"
        #     or key == "sebum"
        #     or key == "Seborrheic Dermatitis"
        #     or key == "inflammation"
        #     or key == "fungi"
        #     or key == "Malassezia"
        #     or key == "microbes"
        # ):
        #     category = "reason"
        # elif key == "greasy" or key == "greasiness":
        #     category = "reason,symptom"
        # elif key == "flaking" or key == "itch" or key == "dry" or key == "oily":
        #     category = "symptom"
        # elif (
        #     key == "zinc"
        #     or key == "ZPT"
        #     or key == "octopirox"
        #     or key == "climbazole"
        #     or key == "Ketoconazole"
        # ):
        #     category = "solution"

        logger.info(category)

        logger.info(item["authors"].split(",")[0])

        hindex = get_hindex_by_author(item["authors"].split(",")[0])

        logger.info(hindex)
        if item["doi"] == "":
            document_url = ""
        else:
            document_url = "https://sci-hub.se/"+item["doi"]
        logger.info(document_url)
        article_info = ArticleInfo(
            item["pmid"],
            item["year"],
            title,
            item["authors"],
            item["journal"],
            item["relative_citation_ratio"],
            item["nih_percentile"],
            item["citation_count"],
            item["field_citation_rate"],
            IF,
            abstract,
            keywords,
            source_url,
            matching_keywords=matching_keywords,
            category=category,
            hindex=hindex,
            doi=item['doi'],
            document_url=document_url
        )
        
        article_info_list.append(article_info)

    data = []
    for article_info in article_info_list:

        # data.append([article_info.pmid, article_info.year,article_info.title,\
        #     article_info.authors,article_info.journal,article_info.rcr,article_info.np,\
        #         article_info.citation,article_info.fcr,article_info.IF,article_info.abstract,article_info.keywords,article_info.source_url])
        data.append(
            [
                article_info.title,
                article_info.keywords,
                article_info.abstract,
                article_info.citation,
                article_info.rcr,
                article_info.journal,
                article_info.IF,
                article_info.hindex,
                article_info.cohindex,
                article_info.authors,
                article_info.year,
                article_info.document_url,
                article_info.source_url,
                article_info.category,
                article_info.matching_keywords,
            ]
        )
    # df = pd.DataFrame(data, columns=["PMID", "Title","Authors","Journal",\
    #     ,"NIH Percentile",,\
    #         "Field Citation Rate",,,])

    # h-index co-author h-index
    df = pd.DataFrame(
        data,
        columns=[
            "Title",
            "Keywords",
            "Abstract",
            "Citation Count",
            "Relative Citation Ratio",
            "Journal",
            "IF",
            "hindex",
            "co-hindex",
            "Authors",
            "Year",
            "Document_url",
            "Source_url",
            "Category",
            "Matching Key Words",
        ],
    )

    csv_filename = "dandruff_info.csv"
    file_exists = pd.io.common.file_exists(csv_filename)
    df.to_csv(csv_filename, mode='a', header=not file_exists, index=False)
    #df.to_csv(csv_filename, mode='w', header=True, index=False)
    logger.info("***************************")
    logger.info("**********Success**********")
    logger.info("***************************")
    return


def get_abstract_keywords_by_pmid(pmid):
    abstract = ""
    keywords_string = ""
    keywords = []
    logger.info("**********Getting abstract and keywords**********")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0"
    }

    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=34575891&retmode=XML
    address = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="
        + str(pmid)
        + "&retmode=XML"
    )
    logger.info(address)
    try:
        f = requests.get(address, headers=headers, timeout=(15, 50))
    except Exception as e:
        return "",""
        
    soup = BeautifulSoup(f.text, features="xml")
    raw_abstract = soup.find("AbstractText")
    if raw_abstract == None:
        abstract = ""
    else:
        abstract = re.sub(r"<.*?>", "", raw_abstract.text)
    logger.info(abstract)

    keyword_list = soup.find("KeywordList")
    if keyword_list == None:
        keywords = ""
    else:
        logger.info(keyword_list)
        for keyword in keyword_list.find_all("Keyword"):

            keyword_text = keyword.text

            keywords.append(keyword_text)

    keywords_string = ",".join(keywords)
    logger.info(keywords_string)
    return abstract, keywords_string


def get_hindex_by_author(name):
    return "N"
    logger.info("**********Getting hindex by author**********")
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


def map_keys_to_categories(input_str):
    key_to_category = {
        "ZPT": "solution",
        "zinc": "solution",
        "octopirox": "solution",
        "climbazole": "solution",
        "Ketoconazole": "solution",
        "greasy": "reason,symptom",
        "greasiness": "reason,symptom",
        "flaking": "symptom",
        "itch": "symptom",
        "dry": "symptom",
        "oily": "symptom",
        "dandruff": "reason",
        "sebum": "reason",
        "Seborrheic Dermatitis": "reason",
        "inflammation": "reason",
        "fungi": "reason",
        "Malassezia": "reason",
        "microbes": "reason",
        "piroctone olamine": 'solution',
    }

    keys = input_str.split(',')
    categories = [key_to_category.get(key, "") for key in keys]

    return ','.join(categories)

def main():
    # key_list = ["dandruff", "sebum", "Seborrheic Dermatitis", "inflammation",
    #             "fungi", "Malassezia", "microbes", "greasy", "greasiness",
    #             "flaking", "itch", "dry", "oily", "zinc", "ZPT",
    #             "octopirox", "climbazole", "Ketoconazole","shampoo","hair conditioner","scalp cleanser"]
    key_list = ["dandruff"
                
                ]
    key_second_list = [""]
    pmid_list_map={}
    
    for key in key_list:
        key_pmid_list=["placeholder"]
        for key2 in key_second_list:
            
            pmid_list = get_article_by_keyword(key, key2)
            
            for pmid in pmid_list:
                if pmid in pmid_list_map:
                    pmid_list_map[pmid].append(key)
                else:
                    pmid_list_map[pmid] = list([key])
    file_name = "pmid_list_map_dandruff.txt"

    with open(file_name, "w") as file:
        for key, value in pmid_list_map.items():
            file.write(f"{key}: {value}\n")
    cnt=0
    
    cur_index=100
    
    
    
    for pmid in pmid_list_map.keys():
        
        
        matching_keywords=pmid_list_map[pmid]
        logger.info(pmid)
        pmid_list=[]
        pmid_list.append(pmid)
        logger.info(pmid_list)
        #TODO now str_matching_keywords only has one matching_keywords
        str_matching_keywords=", ".join(matching_keywords)
        category=map_keys_to_categories(str_matching_keywords)
        logger.info(str_matching_keywords)
        logger.info(category)
        
        
        
        cnt+=1
        get_details_by_pmid(pmid_list=pmid_list, matching_keywords=str_matching_keywords, category=category)

    logger.info(cnt)

    



if __name__ == "__main__":
    main()
