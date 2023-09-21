# search_articles



A simple script to search for articles about *medicine* by keywords and years.



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


