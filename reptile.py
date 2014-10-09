#!/usr/bin/python
# -*- coding: UTF8 -*-

import pycurl
from StringIO import StringIO
import time
import re
import sys
import os
import wordpresslib
import datetime
import MySQLdb

#获取url的id和标题
buffer=StringIO()
c = pycurl.Curl()
c.setopt(c.URL,'http://www.dapenti.com/blog/blog.asp?name=xilei')
c.setopt(c.WRITEDATA,buffer)
c.perform()
c.close()

body=buffer.getvalue()
body=body.decode('GBK').encode('UTF8')

WhichDate=datetime.date.today()
#WhichDate=datetime.date.today()-datetime.timedelta(days=1)
today=WhichDate.strftime('%Y%m%d')

pattern=r'<a href=more.asp\?name=xilei&id=([0-9]*)>【喷嚏图卦'+today+'】(.*?)</a>'


matchObj=re.search(pattern,body,re.M|re.I)
if matchObj:
	print matchObj.group()
else:
	print 'search today poster url failed'
	exit(0)
UrlId=matchObj.group(1)
PosterTitle=matchObj.group(2)
PosterTitle='【图挂'+today+'】'+PosterTitle

#访问链接
buffer=StringIO()
PosterUrl='http://www.dapenti.com/blog/more.asp?name=xilei&id='+UrlId
c=pycurl.Curl()
c.setopt(c.URL,PosterUrl)
c.setopt(c.WRITEDATA,buffer)
c.perform()
c.close()

body=buffer.getvalue()
body=body.decode('GBK').encode('UTF8').replace('\n','')

pattern=r'<P><STRONG>免责申明.*综合编辑 </P>'
matchObj=re.search(pattern,body,re.M|re.I)
if matchObj:
	pass
else:
	print 'search poster failed'
	exit(0)
PosterBody=matchObj.group()
PosterBody=PosterBody.replace("""http://pic.yupoo.com/dapenti/""","""http://proxy.网站.com:8080/m/pic.yupoo.com/dapenti/""")
PosterBody=PosterBody.replace("""http://ptimg.org:88/dapenti/""","""http://proxy.网站.com:8080/m/pic.yupoo.com/dapenti/""")


	
#发表文章，插入到数据库
try:
	db=MySQLdb.connect("ip","用户名","密码","数据库",charset='utf8')
	cur=db.cursor()
	sql="insert into 博客前缀_contents(title,created,modified,text,authorId,allowComment,allowPing,allowFeed) values('%s',unix_timestamp(now()),unix_timestamp(now()),'%s',1,1,1,1)"%(MySQLdb.escape_string(PosterTitle),MySQLdb.escape_string(PosterBody))
	cur.execute(sql)

	sql="select cid from typecho_contents where title like '%s'"%(MySQLdb.escape_string(PosterTitle))
	cur.execute(sql)
	results=cur.fetchall()
	for row in results:
		cid=row[0]

		sql="update typecho_contents set slug='%s' where cid = %s"%(cid,cid)
		print sql
		cur.execute(sql)


except MySQLdb.Error,e:
	print "Mysql Error %d: %s" % (e.args[0], e.args[1])
	db.rollback()

cur.close()		
db.close()

#模版引擎控制


