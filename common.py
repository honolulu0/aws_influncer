import random
import datetime
import pandas as pd
from agents import agents
def getHeader():
    return dict([('Host', None),
                ('Connection', 'keep-alive'),
                ('Upgrade-Insecure-Requests', '1'),
                ('User-Agent', random.choice(agents)),
                ('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'),
                ('Accept-Language', 'en-US,en;q=0.9'),
                ('Accept-Encoding', 'gzip, deflate')])
def getHeader2():
    return dict([('Host', None),
                ('Connection', 'keep-alive'),
                ('Upgrade-Insecure-Requests', '1'),
                ('User-Agent', random.choice(agents)),
                ('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'),
                ('Accept-Language', 'en-US,en;q=0.9'),
                ("content-type", "application/json;charset=utf-8"),
                ('Accept-Encoding', 'gzip, deflate'),
                 ('Authorization',"8ufdvtf7hb4wzwlps5clf0ezwe1jvl2307g7s9vo2ie8cvuyxr")])

def writeLog(type,clue,key,name):
    nowDate = datetime.datetime.now().strftime('%Y-%m-%d')
    # oldContext = FileOperate(dictData="", filepath='./log/', filename='amz_shop_log.log').read_file()
    newContext = (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')+"|"+type+"|"+clue+"|:"+key)+",\n"
    # FileOperate(dictData=newContext, filepath='./log/', filename='amz_shop_log.log').operation_file()
    file = r'./log/'+name+'_'+nowDate+'.log'
    with open(file, 'a+') as f:
        f.write(newContext)


# excelList = {'A': ["关键词"], 'B': ["网红"],'C':["链接"],'D':["粉丝量"],'E':["facebook"],'F':["instgram"]}

def excelBuild(excelList,name):
    df = pd.DataFrame(excelList)
    export_data_to_excel(df, name)
def export_data_to_excel(df,name):    #导出excel
  # encoding编码方式，sheet_name表示要写到的sheet名称， 默认为0， header=None表示不含列名
  df.to_excel("./send_excel/"+name+".xlsx",  sheet_name="first", header=None)
