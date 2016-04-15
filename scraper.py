#!/usr/bin/python
#-*-coding:utf-8-*-

import requests
import bs4
from multiprocessing import Pool
import MySQLdb
import re
import configparser
import os

# 数据库连接
config = configparser.ConfigParser()
config.read('db.ini')
db = config['db']
conn = MySQLdb.connect(host=db['db_host'], user=db['db_user'], passwd=db['db_pass'], db=db['db_database'], port=int(db['db_port']), charset='utf8')
cur = conn.cursor(MySQLdb.cursors.DictCursor)

# 插入数据库数据
def db_insert(data):
    sql_insert = "INSERT INTO iqilu_headlines(`catid`, `title`, `url`, `author`,`image`,`source`, `keywords`, `description`, `content`, `publishtime`) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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

def main():
    for parent,dirnames,filenames in os.walk("rules/"):
        for filename in filenames:
            if filename[-4:] == '.ini':
                config.read("rules/" + filename)
                li = config['list']
                page_urls = get_page_urls(li['url'], li['select'])
                
                for page_url in page_urls:
                    try:
                        db_insert(get_page_data(page_url, config))
                    except Exception,e:
                        print e
                        pass
                        
                conn.commit()
                cur.close()
                conn.close()
                    
    return

# 获取列表页文章链接
def get_page_urls(list_url, select):
    response = requests.get(list_url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    return  [a.attrs.get('href') for a in soup.select(select)]

# 获取内容页内容
def get_page_data(page_url, config):

    data = {}
    data['url'] = page_url
    
    sections = config.sections()
    response = requests.get(page_url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    for section in sections:
        if section != 'list' and section != 'db':
            try:
                select = config[section]['select']
                index = int(config[section]['index'])
                print select
                
                if 'attr' in config[section]:
                    attr = config[section]['attr']
                    data[section] = soup.select(select)[index].attrs.get(attr)
                else:
                    # html格式
                    if 'format' in config[section]:
                        data[section] = filter_tags(soup.select(select)[index].prettify())
                        
                    # 文本格式
                    else:
                        data[section] = soup.select(select)[index].get_text()
                        
                        # 截取字符开始
                        if 'start' in config[section]:
                            start = config[section]['start']
                            start_offset = int(data[section].find(start) + len(start))
                            print 'Start:' + config[section]['start']
                            print 'Start Offset:' + str(start_offset)
                        else:
                            start_offset = None
                        
                        # 截取字符结束
                        if 'end' in config[section]:
                            end = config[section]['end']
                            end_offset = int(data[section].find(end))
                            print 'End:' + config[section]['end']
                            print 'End Offset:' + str(end_offset)
                        else:
                            end_offset = None
                        
                        if(start_offset is not None or end_offset is not None):
                            data[section] = data[section][start_offset:end_offset].strip()
                    #print data[section]
                            
            except IndexError,e:
                print e
                pass
                
    return data

if __name__=='__main__':
    main()
