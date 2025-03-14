from functions import WebInfo

dbuser = ''
dbpassword = ''
host = ''
dbname = ''
table = ''


webInfo = WebInfo(host,dbname,table,dbuser,dbpassword)
webInfo.main()
