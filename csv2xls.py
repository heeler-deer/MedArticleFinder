import pandas as pd


df = pd.read_csv('article_info.csv')


df.to_excel('article_info.xlsx')
