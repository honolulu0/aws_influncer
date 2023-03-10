import json
import threading
import time


import random

import requests
import datetime

import urllib3
from lxml import etree
from agents import agents
from bs import bs
import math
import common


def handle_request_err(status_code):
    if status_code == 503:
        print('被反爬虫拦截，休眠30分钟')
        time.sleep(1800)
def handle_random_sleep():
    index = random.randint(0,60)
    time.sleep(index)

# 配自己的代理
proxies ={

}
internalData = []
searchData = {}


def best_sellers(url):   #排行榜爬虫
    headers = getHeader()
    r = requests.get(url,
                     data=None,
                     headers=headers,
                     #proxies=proxies,
                     verify=False)
    if r.status_code == 200:
        return r.text
    else:
        handle_request_err(r.status_code)
        return None

def inner_search(param):
    headers = common.getHeader()
    url = 'https://www.amazon.com' + param

    r = requests.get(url,
                     data=None,
                     headers=headers,
                     #proxies=proxies,
                     verify=False)
    if r.status_code == 200:
        return r.text
    else:
        handle_request_err(r.status_code)
        return None


def search(keys):
    headers = common.getHeader()
    url = 'https://www.amazon.com/s?k='
    if len(keys) > 0:
        keysList = keys[0].split(" ")
        for key in keysList:
            url += key + "+"
        url = url[:len(url) - 1]
        print(url)
        r = requests.get(url,
                         data=None,
                         headers=headers,
                         # proxies=proxies,
                         verify=False)
        if r.status_code == 200:
            return r.text
        else:
            handle_request_err(r.status_code)
            return None
    else:
        return None

spider = 0
def nextPage(html):  #是否存在翻页按钮(能点的)
    href = html.xpath(
        '//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]/@href'
    )
    return href
def dataDeal(keyId, els,html):
    url = html.xpath(
        '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]/@href')
    # shop-influencer-profile-name
    try:
        for item in url:
            inner_rsp = inner_search(item)
            if inner_rsp:
                inner_html = etree.HTML(inner_rsp)
                shops = inner_html.xpath('//div[@class="a-profile-avatar-wrapper"]/../@href')
                for shop in shops:
                    # getSpider()
                    if "/shop/" in shop:
                        influncer = shop[shop.find("/shop/") + 6:]
                        if influncer in internalData:
                            pass
                        else:
                            nameArr = getName(shop)
                            print("asdasdasdn", nameArr)
                            print("len(nameArr)", len(nameArr))
                            if len(nameArr) > 0:
                                influncer = influncer + "##&*%$#" + nameArr[0]
                            internalData.append(influncer)
                        print(influncer)
                        searchData[json.dumps(els)] = internalData
                pass
            else:
                print("解析Video标签内数据出错" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
            # print(internalData)
        print("轮询结束:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        print("end:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        updateSpider(keyId, searchData, els, 1, False)
        nextP = nextPage(html)
        if len(nextP) > 0:  # 判断是否有下一页
            readUrl(keyId, els, nextP)
        # 存储数据
        updateSpider(keyId, searchData, els, 1, True)
        # threading.Timer(1, run)
    except Exception as e:
        print("中断...:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), e)
        run()
    finally:
        print("最后结束时间：" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        run()
def readUrl(keyId,key,urlList):
    # print(urlList[0])
    urlPage = "https://www.amazon.com" + urlList[0]
    rsp = best_sellers(urlPage)
    html = etree.HTML(rsp)
    dataDeal(keyId, key, html)
def run():     #爬虫主线程
    global searchData,internalData
    # setSpider(1)
    keysData = getKeys()
    els = keysData["keys"]
    keyId = keysData["id"]
    print("正在爬取keys:",els)
    if els:
        searchData = {}
        rsp = search(els)
        if rsp:
            internalData = []
            html = etree.HTML(rsp)
            dataDeal(keyId,els,html)
        else:
            print("没能搜索到内页数据"+ datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    else:
        print("finish"+ datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        timeToPoint()

def getName(shop):
    headers = common.getHeader()
    url = 'https://www.amazon.com'+shop
    r = requests.get(url,
                     data=None,
                     headers=headers,
                     # proxies=proxies,
                     verify=False)
    if r.status_code == 200:
        html = etree.HTML(r.text)
        name = html.xpath('//div[@id="shop-influencer-profile-name"]/text()')
        return name
    else:
        return None
def export_data_to_excel(df):    #导出excel
  # encoding编码方式，sheet_name表示要写到的sheet名称， 默认为0， header=None表示不含列名
  df.to_excel("./testex.xlsx", encoding="utf_8_sig", sheet_name="first", header=None)

def timeToPoint():   #定时器在特定时间触发爬虫
    nowDate = datetime.datetime.now()
    nowDateTime = datetime.datetime.strftime(nowDate,'%H:%M:%S')
    print(datetime.datetime.strftime(nowDate,'%H:%M:%S'))
    startTime = "10:00:00"
    if startTime == nowDateTime:
        run()
    else :
        timer = threading.Timer(1, timeToPoint)
        timer.start()
        pass
def setSpider(type):    #更新心跳
    global spider
    spider = type
    return spider
def getSpider():    #获取心跳
    # print("buging",spider)
    return spider

#isendup 是否最后更新
def updateSpider(id,data,key,type,isendup):
    headers = common.getHeader()
    url = 'https://ebus-b1.test.api.sui10.com/json/amazon/update'
    if type == 2 :
        influncers = data[key]
    else :
        influncers = data[json.dumps(key)]
    print("influncersinfluncers",influncers)
    jsonData = {
        "req":{
            "token":"",
            "id":id,
            "influncers":influncers,
            "timestamp":time.time()
        }
    }
    r = requests.get(url,
                     data=json.dumps(jsonData),
                     headers=headers,
                     # proxies=proxies,
                     verify=False)
    # jsonData = json.loads(r.content)
    if r.status_code == 200:
        print("ok")
        if isendup:
            run()
    else:
        return None
def getKeys():   #获取关键字
    headers = common.getHeader()
    url = 'https://ebus-b1.test.api.sui10.com/json/amazon/key'
    r = requests.get(url,
                     data='{"req": {"token": ""}}',
                     headers=headers,
                     # proxies=proxies,
                     verify=False)

    jsonData = json.loads(r.content)
    if r.status_code == 200:
        return jsonData['rsp']
    else:
        return None

def receive(socket, signal):
    while signal:
        try:
            data = socket.recv(99048)
            print(str(os.getpid()) + "接收到服务端数据: " + str(data.decode("utf-8")))
            keyData = json.loads(str(data.decode("utf-8")))
            print("keyDatass",keyData)
            keys = keyData["keys"]
            keyId = keyData["id"]
            if 'keys' in keyData and 'id' in keyData:
                if len(keys) > 0:  # 判断是否有keys存在
                    for ki in keys:
                        parse_youtube(keyId,ki)
                else:
                    logInfo = {"id": keyId, "keys": keys}

                socket.close()
            sys.exit(0)
        except Exception as e:
            print("服务端已主动断开链接")
            break

def main():
    print("我是爬虫客户端进程, pid=" + str(os.getpid()))
    host = "localhost"
    port = 31999
    #Attempt connection to server
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    except:
        print("无法链接服务端")
        sys.exit(0)

    receiveThread = threading.Thread(target = receive, args = (sock, True))
    receiveThread.start()

    while True:
        message = "这是" + str(os.getpid()) +"爬出来的结果..."
        time.sleep(5)
        sock.sendall(str.encode(message))

if __name__ == '__main__':   #入口函数
    urllib3.disable_warnings()
    print("begin:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    main()




