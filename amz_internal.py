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
proxies ={
    'http': "http://127.0.0.1:1087",
    'https': "http://127.0.0.1:1087"
}
internalData = []
searchData = {}
def best_sellers(url):   #排行榜爬虫
    headers = common.getHeader()
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
        print(r.text)
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
def influncerDeal(shops,key):   #第一页和分页的处理
    global searchData, internalData
    for shop in shops:
        # getSpider()
        if "/shop/" in shop:
            influncer = shop[shop.find("/shop/") + 6:]
            if influncer in internalData:
                pass
            else:
                nameArr = getName(shop)
                if len(nameArr) > 0:
                    influncer = influncer + "##&*%$#" + nameArr[0]
                internalData.append(influncer)
            print(influncer)
            searchData[json.dumps(key)] = internalData
def getDataDeal(keyId,key,url):
    try:
        for item in url:
            inner_rsp = inner_search(item)
            if inner_rsp:
                inner_html = etree.HTML(inner_rsp)
                shops = inner_html.xpath('//div[@class="a-profile-avatar-wrapper"]/../@href')
                influncerDeal(shops,key)
                pass
            else:
                print("解析Video标签内数据出错")
            # print(internalData)
        print("分页轮询结束:"+ datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        nextP = nextPage(html)
        if (len(nextP)):  # 判断是否有下一页
            updateSpider(keyId, searchData, els, 1,False)
            readUrl(keyId, key, nextP)
    except Exception as e:
        print("中断...:"+ datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), e)
        #重跑当前页
        readUrl(keyId, key, urlList[0])
def readUrl(keyId,key,urlList):
    urlPage = "https://www.amazon.com" + urlList[0]
    rsp = best_sellers(urlPage)
    html = etree.HTML(rsp)
    url = html.xpath(
        '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]/@href')
    getDataDeal(keyId,key,url)

def ShopDataDeal(url,searchData,keyId,els):
    for item in url:
        inner_rsp = inner_search(item)
        if inner_rsp:
            inner_html = etree.HTML(inner_rsp)
            shops = inner_html.xpath('//div[@class="a-profile-avatar-wrapper"]/../@href')
            influncerDeal(shops,els)
            pass
        else:
            print("解析Video标签内数据出错" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    print("轮询结束:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    updateSpider(keyId, searchData, els, 1, False)
    nextP = nextPage(html)
    if len(nextP) > 0:  # 判断是否有下一页
        readUrl(keyId, els, nextP)
    # 存储数据
    updateSpider(keyId, searchData, els, 1, True)
def run():     #爬虫主线程
    # setSpider(1)
    global searchData,internalData
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

            url = html.xpath(
                '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]/@href')
            # shop-influencer-profile-name
            try:
                ShopDataDeal(url,searchData,keyId,els)
                # threading.Timer(1, run)
            except Exception as e:
                print("中断...:"+ datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),e)
                run()
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

if __name__ == '__main__':   #入口函数
    urllib3.disable_warnings()
    print("begin:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    urlCount = 0  #爬取的url列表
    shopsCount = 0 #shup数组
    while(True):
        run()



