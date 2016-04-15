# python-caiji
使用python采集网页，可以自定义列表、内容规则

## 数据库配置
在db.ini文件中，配置db段，例如：
[db]
db_port = 3306
db_user = user
db_host = localhost
db_pass = password
db_database = database

## 规则配置
在rules下,以.ini结尾的文件。
一个INI文件代表一个采集站点。
一个样例网站配置如下：
[list]
url = http://news.xxx.com/list/1227.html
select = .zlefta h3 a

[title]
select = h2
index = 1

[keywords]
select = meta[name="keywords"]
index = 0
attr = content

[description]
select = meta[name="description"]
index = 0
attr = content

[publishtime]
select = .zleftc
index = 0
end = 来源

[source]
select = .zleftc
index = 0
start = 来源：

[content]
select = .zleftf
index = 0
format = html

[image]
select = .zleftf img
index = 0
attr = src

[author]
select = .zleftg
index = 0
start = 编辑：
end = 责任编辑：

