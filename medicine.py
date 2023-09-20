import pandas as pd
import glob
import requests
import time
from bs4 import BeautifulSoup
from pygtrans import Translate
import time
import json
from lxml import html






article_info_list = []




class ArticleInfo:
    def __init__(self, pmid, year,title,authors,journal,rcr,np,citation,fcr,IF):

        self.pmid = pmid
        self.year=year
        self.title=title
        self.authors=authors
        self.journal=journal
        self.rcr=rcr
        self.np=np
        self.citation=citation
        self.fcr=fcr
        self.IF=IF
        




def get_IF_from_name(name):
    # 从期刊名查询impact factor
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
    }
    name.replace(' ', '+')  # 在网址查询时把空格转为+号
    address = "http://sci.justscience.cn/list?q=" + str(name) + "&sci=1"+"&research_area=&If_range_min=&If_range_max=&jcr_quartile=0&oa=2&Self_cites_ratio_min=&Self_cites_ratio_max=&mainclass=0&subclass=0&pub_country=&not_pub_country=&sci_type=2&pub_frequency=7&adv=1"
    print(address)
    f = requests.get(address, headers = headers, timeout=(3,7)) # 加timeout防掉线

    parsed_html = html.fromstring(f.content)

    #    使用XPath来定位目标元素
    tr_elements = parsed_html.xpath("/html/body/div[1]/div[1]/div[2]/div[2]/table/tbody/tr")



    for tr in tr_elements:
        print("::::::::::::::::::::::::::")
    # 使用XPath定位当前<tr>元素下的第一个<td>元素的文本内容
        row_data = tr.xpath("td[1]/a/text()")
        row_data2 = tr.xpath("td[2]/text()")
        row_data=str(row_data[0])
        row_data2=str(row_data2[0])
        print(row_data.strip().upper())
        
        print(name.strip().upper())
        if(row_data.strip().upper()==name.strip().upper() or row_data2.strip().upper()==name.strip().upper()):
            time.sleep(1)
            print(tr.xpath("td[7]/text()")[0])
            
            return tr.xpath("td[7]/text()")[0]
        



def get_article_by_keyword():
    pmid_result_list=[]
    key_first=["microbes"]
    key_second=["shampoo"]
    key_year=[2012]
    #https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=science%5bjournal%5d+AND+breast+cancer+AND+2008
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
    }
    print("************Getting pmid of article*****************")
    for key in key_first:
        for key2 in key_second:
            for key3 in key_year:
                address="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmax=20&term=%5bjournal%5d+AND+" 
                address=address+key+"+"+key2+"+AND+"+str(key3)
                print(address)
                f = requests.get(address, headers = headers, timeout=(3,7))
                soup = BeautifulSoup(f.text, features="xml")
                # 提取 Count 元素的内容
                count = soup.find("Count").text
                print("|  Count  |  key1  |  key2  |  key3  |")
                print("|  "+str(count)+"  |  " +str(key) + "  |  "+ str(key2) +"  |  "+str(key3)+"  |")

                # 提取 IdList 中的 Id 元素内容
                id_list = soup.find_all("Id")
                for id_element in id_list:
                    print("Id:", id_element.text)
                    pmid_result_list.append(id_element.text)
                print(pmid_result_list)
                time.sleep(1.5)
                
    
    return pmid_result_list
                


def get_details_by_pmid(pmid_list):
    
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
    }
    #https://icite.od.nih.gov/api/pubs?pmids=28968381,28324054,23843509&fl=pmid,year,title,apt,relative_citation_ratio,cited_by_clin
    print("************Getting details by pmid******************")
    address="https://icite.od.nih.gov/api/pubs?pmids="+ ",".join(pmid_list)+\
        "&fl=pmid,year,title,authors,journal,relative_citation_ratio,nih_percentile,citation_count,field_citation_rate"
    print(address)
    print("\n")
    f = requests.get(address, headers = headers, timeout=(3,7))
    response=f.text
    soup = json.loads(response)
    
    for item in soup["data"]:
        print("PMID:", item["pmid"])
        print("Year:", item["year"])
        print("Title:", item["title"])
        print("Authors:", item["authors"])
        print("Journal:", item["journal"])
        print("Relative Citation Ratio:", item["relative_citation_ratio"])
        print("NIH Percentile:", item["nih_percentile"])
        print("Citation Count:", item["citation_count"])
        print("Field Citation Rate:", item["field_citation_rate"])
        IF=get_IF_from_name(item["journal"])
        if(IF==None):IF="N"
        print("Impact Factor:",IF)        
        
        
        
        article_info = ArticleInfo(item["pmid"],item["year"],item["title"],item["authors"],item["journal"],item["relative_citation_ratio"],item["nih_percentile"],item["citation_count"], item["field_citation_rate"],IF)
        
        
        
        article_info_list.append(article_info)
        print("\n\n\n")
        
    
    # 创建一个包含文章信息的DataFrame
    data = []
    for article_info in article_info_list:
        
        data.append([article_info.pmid, article_info.year,article_info.title,article_info.authors,article_info.journal,article_info.rcr,article_info.np,article_info.citation,article_info.fcr,article_info.IF])

    df = pd.DataFrame(data, columns=["PMID", "Year","Title","Authors","Journal","Relative Citation Ratio","NIH Percentile","Citation Count","Field Citation Rate","IF"])


    # 指定要保存CSV文件的文件名
    csv_filename = "article_info.csv"

    # 将DataFrame保存为CSV文件
    df.to_csv(csv_filename, index=False)
    
    return
















pmid_list=get_article_by_keyword()
get_details_by_pmid(pmid_list=pmid_list)