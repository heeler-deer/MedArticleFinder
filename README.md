# MedArticleFinder







## Search articles about medicine


A simple script to search for articles about **medicine** by keywords and years.



By using these sites:

```shell
http://sci.justscience.cn/list?q=
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
https://icite.od.nih.gov/api/pubs
https://sci-hub.se/
https://scholar.google.com/
```
and [scholarly](https://github.com/scholarly-python-package/scholarly), we can easily get details about articles,like:

```shell
title
authors
years
keywords
abstract
Citation Count
Relative Citation Ratio
Journal
IF
h-index
```

**NOTE!!!!!!**
While there may be duplicate names, it's important to note that the code cannot guarantee the absolute reliability of the h-index.



After we get details, we can easily convert data to csv files.




It's easily to modiy the keywords in function `main()`:


```python
key_list = ["inflammation"]
key_second_list = ["shampoo"]
```



And you can set year in function `get_article_by_keyword(key, key2)`:


```python
key_year = [2013]
```


or you can just send params like that:


```shell
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?term=%5bjournal%5d+AND+Seborrheic%20Dermatitis+shampoo+AND+(%222012/01/01%22[Date%20-%20Publication]%20:%20%222023/12/31%22[Date%20-%20Publication])
```





## Download articles



By using [scihub.py](https://github.com/zaytoun/scihub.py), we can easily download papers by building their sci-hub url:


```
https://sci-hub.se/+doi
```


then we just use scihub.py in `download_article.py`:


```python
def download_paper(url,title):
    sh = SciHub()
    logger.info("*****************Getting paper by scihub url**********")
    # exactly the same thing as fetch except downloads the articles to disk
    # if no path given, a unique name will be used as the file name
    try:
        logger.info(title)
        logger.info(url)
        result = sh.download(url, path='./paper/'+title+".pdf")
        logger.info("**************************")
        logger.info("**********Success*********")
        logger.info("**************************")
        return "Y"
    except Exception as e:
        logger.error("Can't find url")
        return ""
```

After several seconds, we can get the pdf version of the paper.