#!/usr/bin/python
#-*-coding:utf-8-*-

import requests
import bs4
from multiprocessing import Pool
import MySQLdb
import re
import configparser
import os

# 采集地址
root_url = 'http://news.sdchina.com'
list_url = root_url + '/list/1227.html'

# 数据库连接
dbc = configparser.ConfigParser()
realPath = os.path.split(os.path.realpath(__file__))[0]
dbc.read(realPath + '/db.ini')
conn = MySQLdb.connect(host=dbc.get("db", 'db_host'), user=dbc.get("db", 'db_user'), passwd=dbc.get("db", 'db_pass'), db=dbc.get("db", 'db_database'), port=int(dbc.get("db", 'db_port')), charset='utf8')
cur = conn.cursor(MySQLdb.cursors.DictCursor)

# 插入数据库数据
def db_insert(data):
    sql_insert = "INSERT INTO table(`catid`, `title`, `url`, `author`,`image`,`source`, `keywords`, `description`, `content`, `publishtime`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cur.execute(sql_insert, (829, data['title'], data['url'], data['author'], data['image'], data['source'], data['keywords'], data['description'], data['content'], data['publishtime']))
    return

# 过滤script style iframe等标签
def filter_tags(htmlstr):
    re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)
    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)
    re_iframe = re.compile('<\s*iframe[^>]*>[^<]*<\s*/\s*iframe\s*>', re.I)
    s = re_script.sub('', htmlstr)
    s = re_style.sub('', s)
    s = re_iframe.sub('', s)
    return s

# 获取列表页文章链接
def get_page_urls():
    response = requests.get(list_url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    return  [a.attrs.get('href') for a in soup.select('.zlefta h3 a')]

# 获取内容页内容
def get_page_data(page_url):
    data = {}
    response = requests.get(page_url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    data['url'] = page_url
    data['title'] = soup.select('h1')[1].get_text()
    data['keywords'] = soup.select('meta[name="keywords"]')[0].attrs.get('content')
    data['description'] = soup.select('meta[name="description"]')[0].attrs.get('content')
    pt = soup.select('.zleftc')[0].get_text()
    data['publishtime'] = pt[:pt.find(u'来源')].strip()
    source = soup.select('.zleftc')[0].get_text()
    data['source'] = source[source.find(u'来源：')+3:].strip()
    data['content'] = filter_tags(soup.select('.zleftf')[0].prettify())
    images = soup.select('.zleftf img')
    if images:
        data['image'] = images[0].attrs.get('src')
    else:
        data['image'] = ''
    data['author'] = soup.select('.zleftg')[0].get_text()
    return data

# 入口
def show_stats():
    # pool = Pool(8)
    page_urls = get_page_urls()
    #results = pool.map(get_page_data, page_urls)

    for page_url in page_urls:
        try:
            data = get_page_data(page_url)
            db_insert(data)
        except Exception,e:
            print e
            continue
    conn.commit()
    cur.close()
    conn.close()

#if __name__=='__main__':
show_stats()
