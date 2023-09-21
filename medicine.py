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


# 创建一个colorlog日志记录器
logger = colorlog.getLogger()
logger.setLevel(logging.DEBUG)

# 创建一个控制台处理程序，并设置颜色格式化程序
console_handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
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

# 创建一个文件处理程序，将日志写入文件
file_handler = logging.FileHandler('medicine.log', mode='w')
file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)

# 将控制台处理程序和文件处理程序添加到日志记录器
logger.addHandler(console_handler)
logger.addHandler(file_handler)
# 文章信息
article_info_list = []


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
        self.doi=doi
        self.document_url = document_url
        self.category = category
        self.matching_keywords = matching_keywords
        self.hindex = hindex
        self.cohindex = "N"
        


def get_IF_from_name(name):
    # 从期刊名查询impact factor
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0"
    }
    name.replace(" ", "+")  # 在网址查询时把空格转为+号
    address = (
        "http://sci.justscience.cn/list?q="
        + str(name)
        + "&sci=1"
        + "&research_area=&If_range_min=&If_range_max=&jcr_quartile=0&oa=2&Self_cites_ratio_min=&Self_cites_ratio_max=&mainclass=0&subclass=0&pub_country=&not_pub_country=&sci_type=2&pub_frequency=7&adv=1"
    )
    logger.info(address)
    f = requests.get(address, headers=headers, timeout=(3, 7))  # 加timeout防掉线

    parsed_html = html.fromstring(f.content)

    #    使用XPath来定位目标元素
    tr_elements = parsed_html.xpath(
        "/html/body/div[1]/div[1]/div[2]/div[2]/table/tbody/tr"
    )

    for tr in tr_elements:
        logger.info("::::::::::::::::::::::::::")
        # 使用XPath定位当前<tr>元素下的第一个<td>元素的文本内容
        row_data = tr.xpath("td[1]/a/text()")
        row_data2 = tr.xpath("td[2]/text()")
        row_data = str(row_data[0])
        row_data2 = str(row_data2[0])
        logger.info(row_data.strip().upper())

        logger.info(name.strip().upper())
        if (
            row_data.strip().upper() == name.strip().upper()
            or row_data2.strip().upper() == name.strip().upper()
        ):
            time.sleep(1)
            logger.info(tr.xpath("td[7]/text()")[0])

            return tr.xpath("td[7]/text()")[0]


def get_article_by_keyword(key, key2):
    pmid_result_list = []

    key_year = [2013]
    # https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=science%5bjournal%5d+AND+breast+cancer+AND+2008
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0"
    }
    logger.info("************Getting pmid of article*****************")
    for key3 in key_year:
        address = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=20&term=%5bjournal%5d+AND+"
        address = address + key + "+" + key2 + "+AND+" + str(key3)
        logger.info(address)
        f = requests.get(address, headers=headers, timeout=(3, 7))
        soup = BeautifulSoup(f.text, features="xml")
        # 提取 Count 元素的内容
        count = soup.find("Count").text
        logger.info("|  Count  |  key1  |  key2  |  key3  |")
        logger.info(
            "|  "
            + str(count)
            + "  |  "
            + str(key)
            + "  |  "
            + str(key2)
            + "  |  "
            + str(key3)
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
        # 提取 IdList 中的 Id 元素内容
        id_list = soup.find_all("Id")
        for id_element in id_list:
            logger.info("Id:"+ id_element.text)
            
            pmid_result_list.append(id_element.text)
        logger.info("%s",pmid_result_list)
        
        time.sleep(1.5)
        

    return pmid_result_list


def get_details_by_pmid(pmid_list, key, key2):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0"
    }
    if pmid_list[0] == "error":

        return
    # https://icite.od.nih.gov/api/pubs?pmids=28968381,28324054,23843509&fl=pmid,year,title,apt,relative_citation_ratio,cited_by_clin
    logger.info("************Getting details by pmid******************")
    address = (
        "https://icite.od.nih.gov/api/pubs?pmids="
        + ",".join(pmid_list)
        + "&fl=pmid,year,title,authors,journal,relative_citation_ratio,nih_percentile,citation_count,field_citation_rate,doi"
    )
    logger.info(address)
    f = requests.get(address, headers=headers, timeout=(3, 7))
    response = f.text
    soup = json.loads(response)

    for item in soup["data"]:
        logger.info("PMID:"+ str(item["pmid"]))
        
        logger.info("Year:"+ str(item["year"]))
        logger.info("Title:"+ item["title"])
        logger.info("Authors:"+ item["authors"])
        logger.info("Journal:"+ item["journal"])
        logger.info("Relative Citation Ratio:"+
                    str(item["relative_citation_ratio"]))
        logger.info("NIH Percentile:"+ str(item["nih_percentile"]))
        logger.info("Citation Count:" +str(item["citation_count"]))
        logger.info("Field Citation Rate:"+ str(item["field_citation_rate"]))
        logger.info("DOI:"+str(item["doi"]))
        # build IF,source_url,abstract,keywords,document_url

        IF = get_IF_from_name(item["journal"])
        if IF == None:
            IF = "N"
        logger.info("Impact Factor:"+ IF)
        source_url = "https://pubmed.ncbi.nlm.nih.gov/" + \
            str(item["pmid"]) + "/"

        abstract, keywords = get_abstract_keywords_by_pmid(item["pmid"])

        logger.info(key)
        category = ""
        if (
            key == "dandruff"
            or key == "sebum"
            or key == "Seborrheic Dermatitis"
            or key == "inflammation"
            or key == "fungi"
            or key == "Malassezia"
            or key == "microbes"
        ):
            category = "reason"
        elif key == "greasy" or key == "greasiness":
            category = "reason,symptom"
        elif key == "flaking" or key == "itch" or key == "dry" or key == "oily":
            category = "symptom"
        elif (
            key == "zinc"
            or key == "ZPT"
            or key == "octopirox"
            or key == "climbazole"
            or key == "Ketoconazole"
        ):
            category = "solution"

        logger.info(category)

        logger.info(item["authors"].split(",")[0])

        hindex = get_hindex_by_author(item["authors"].split(",")[0])

        logger.info(hindex)
        if item["doi"]=="":
            document_url=""
        else:
            document_url="https://sci-hub.se/"+item["doi"]
        logger.info(document_url)
        article_info = ArticleInfo(
            item["pmid"],
            item["year"],
            item["title"],
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
            matching_keywords=key,
            category=category,
            hindex=hindex,
            doi=item['doi'],
            document_url=document_url
        )

        article_info_list.append(article_info)
    
    # 创建一个包含文章信息的DataFrame
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
    # 指定要保存CSV文件的文件名
    csv_filename = "article_info.csv"

    # 将DataFrame保存为CSV文件
    df.to_csv(csv_filename, index=False)
    logger.info("*******************Success*****************")
    return


def get_abstract_keywords_by_pmid(pmid):
    abstract = ""
    keywords_string = ""
    keywords = []
    logger.info("*********Getting abstract and keywords********")
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
    f = requests.get(address, headers=headers, timeout=(3, 7))
    soup = BeautifulSoup(f.text, features="xml")
    raw_abstract = soup.find("AbstractText").text
    if raw_abstract == None:
        abstract = ""
    else:
        abstract = re.sub(r"<.*?>", "", raw_abstract)
    logger.info(abstract)

    keyword_list = soup.find("KeywordList")
    if keyword_list == None:
        keywords = ""
    else:
        logger.info(keyword_list)
        #   创建一个空列表来存储关键字

        # 遍历所有的Keyword元素
        for keyword in keyword_list.find_all("Keyword"):
            # 获取关键字的文本内容
            keyword_text = keyword.text
            # 将关键字文本添加到关键字列表中
            keywords.append(keyword_text)

    keywords_string = ",".join(keywords)
    logger.info(keywords_string)
    return abstract, keywords_string


def get_hindex_by_author(name):
    logger.info("**************Getting hindex by author*****************")
    try:
        search_query = scholarly.search_author(name)

        author = next(search_query)

        scholarly.pprint(scholarly.fill(author, sections=["indices"]))
        hindex = scholarly.fill(author, sections=["indices"])["hindex"]
        if hindex == None:
            logger.error("**********No hindex as hindex==None*******")
            hindex = "N"
        logger.info(hindex)
        random_integer = random.randint(2, 4)
        time.sleep(random_integer)
        return hindex
    except Exception as e:
        logger.error("**********No hindex as got exception*******")
        hindex = "N"
        return hindex


# get_abstract_keywords_by_pmid(34575891)
def main():
    key_list = ["inflammation"]
    key_second_list = ["shampoo"]
    for key in key_list:
        for key2 in key_second_list:

            pmid_list = get_article_by_keyword(key, key2)
            if pmid_list[0] == "error":
                logger.error("error")
                continue
            else:
                get_details_by_pmid(pmid_list=pmid_list, key=key, key2=key2)


if __name__ == "__main__":
    main()
