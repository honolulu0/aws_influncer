
import json
import threading
import time
import random

import requests
import datetime
import common
import urllib3
from lxml import etree
from agents import agents
from bs import bs
import math
from urllib import parse


def handle_request_err(status_code):
    if status_code == 503:
        print('被反爬虫拦截，休眠30分钟')
        time.sleep(1800)
def handle_random_sleep():
    index = random.randint(0,60)
    time.sleep(index)

def getHeader():
    index = random.randint(0,len(agents)-1)
    handle_random_sleep()
    return dict([('Host', None),
                ('Connection', 'keep-alive'),
                ('Upgrade-Insecure-Requests', '1'),
                ('User-Agent', agents[index]),
                ('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'),
                ('Accept-Language', 'en-US,en;q=0.9'),
                ('Accept-Encoding', 'gzip, deflate')])

def getKeys():   #获取关键字
    headers = getHeader()
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

def search(keys):
    headers = getHeader()
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

def inner_search(param):
    headers = getHeader()
    url = 'https://www.amazon.com' + param
    # url = "https://www.amazon.com/Emergency-Adjustable-Commercial-Hardwired-Certified/dp/B09CGP2WMW/ref=dp_prsubs_2?pd_rd_w=Ym4vh&content-id=amzn1.sym.ec3cee7c-6bd8-496a-8166-4fdb6d51cad1&pf_rd_p=ec3cee7c-6bd8-496a-8166-4fdb6d51cad1&pf_rd_r=0TPBCP2XZPFNWMVGXX8A&pd_rd_wg=1Pjfl&pd_rd_r=a304fd6b-4959-46dc-8375-b36af7aca5cd&pd_rd_i=B09CGP2WMW&th=1"
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
def read_next(href):
    headers = getHeader()
    url = "https://www.amazon.com" + href
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
def shopInfo(query):
    headers = getHeader()
    url = "https://www.amazon.com"+query
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
def nextPage(html):  #是否存在翻页按钮(能点的)
    href = html.xpath(
        '//a[@class="s-pagination-item s-pagination-next s-pagination-button s-pagination-separator"]/@href'
    )
    return href


def updataEvent(data):
    headers = getHeader()
    url = "https://ebus-b1.test.api.sui10.com/json/amz_seller/update"
    print("ssss",data)
    jsonData = {
        "req":{
            "token": "",
            "name": data["soldName"],
            "data": json.dumps(data)
        }
    }
    r = requests.get(url,
                     data=json.dumps(jsonData),
                     headers=headers,
                     # proxies=proxies,
                     verify=False)
    if r.status_code == 200:
        common.writeLog("tips", "updataEvent", data["soldName"] + "save success","amz_shop_log")
        return r.text
    else:
        common.writeLog("error", "updataEvent", data["soldName"] + "save fail","amz_shop_log")
        handle_request_err(r.status_code)
        return None

def dataDeal(inner_rsp,els):
    inner_html = etree.HTML(inner_rsp)
    # Brand: 之后或者 the后面store之前
    soldName = inner_html.xpath('//a[@id="sellerProfileTriggerId"]/text()')
    soldHref = inner_html.xpath('//a[@id="sellerProfileTriggerId"]/@href')
    brand = inner_html.xpath('//a[@id="bylineInfo"]/text()')
    brandLink = inner_html.xpath('//a[@id="bylineInfo"]/@href')
    moneyArr = inner_html.xpath(
        '//span[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span[@class="a-offscreen"]/text()')
    money = "0"
    if len(moneyArr) > 0:
        money = moneyArr[0]
    print("money", money)
    proInfoth = inner_html.xpath('//th[@class="a-color-secondary a-size-base prodDetSectionEntry"]/text()')
    proInfotd = inner_html.xpath('//td[@class="a-size-base prodDetAttrValue"]/text()')
    # proInfotdss = inner_html.xpath('//head/following-sibling::*[0]/text()')
    shopTitle = inner_html.xpath('//span[@id="productTitle"]/text()')
    shipsFrom = inner_html.xpath("//span[@class='a-size-small tabular-buybox-text-message']/text()")
    ASIN = ""
    CountryofOrigin = ""
    print("proInfoth", len(proInfoth))
    for i in range(len(proInfoth)):
        if (i + 1) <= len(proInfotd):
            if "ASIN" in proInfoth[i]:
                ASIN = proInfotd[i]
            if "Country of Origin" in proInfoth[i]:
                print("CountryofOrigin", proInfotd, len(proInfotd), i)
                CountryofOrigin = proInfotd[i]
    # Best Sellers Rank
    productDetai = inner_html.xpath("//table[@id='productDetails_detailBullets_sections1']//td//span//span//a/text()")
    if len(soldHref) > 0:
        result = parse.urlparse(soldHref[0])
        query_dict = parse.parse_qs(result.query)
        seller = query_dict["seller"][0]
        # print("proInfo",soldName,soldHref,brand)

        shopData = shopInfo(soldHref[0])
        shop_html = etree.HTML(shopData)
        AOKETE = shop_html.xpath("//span[@id='seller-contact-button']//span//a/@href")
        business = shop_html.xpath(
            "//div[@id='page-section-detail-seller-info']//div[@class='a-column a-span12 a-spacing-none']//div[@class='a-box a-spacing-none a-color-base-background box-section']//div[@class='a-box-inner a-padding-medium']//div[@class='a-row a-spacing-none']//span/text()")
        businessName = ""
        if len(business) > 1:
            businessName = business[1]
        businessAddress = shop_html.xpath("//div[@class='a-row a-spacing-none indent-left']//span/text()")
        country = businessAddress[len(businessAddress) - 1]
        address = ""
        for a in range(len(businessAddress)):
            if a < len(businessAddress) - 1:
                address = address + businessAddress[a]
        brandText = ""
        if len(brand) > 0:
            brandText = brand[0]
        infoData = {
            "soldName": soldName[0],
            "soldHref": soldHref[0],
            "brand": brandText,
            "ASIN": ASIN,
            "CountryofOrigin": CountryofOrigin,
            "productDetai": productDetai,
            "els": els[0],  # 关键词
            "seller": seller,
            "address": address,
            "country": country,
            "businessName": businessName,
            "AOKETE": AOKETE[0],  # 聊天链接
            "shopTitle": shopTitle[0],
            "brandLink": "https://www.amazon.com/" + brandLink[0],
            "shipsFrom": shipsFrom[0],
            "money": money,

        }
        return infoData
# def nextPageRead(key,nhref):
#     rsp = read_next(nhref[0])
#     if rsp:
#         html = etree.HTML(rsp)
#         url = html.xpath(
#             '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]/@href')
#         try:
#             for item in url:
#                 inner_rsp = inner_search(item)
#                 if inner_rsp:
#                     infoData = dataDeal(inner_rsp)
#                     updataEvent(infoData)
#             nextP = nextPage(html)
#             if (len(nextP)):  # 判断是否有下一页
#                 common.writeLog("tips", "nextPageRead", "next page:"+key[0],"amz_shop_log")
#                 nextPageRead(key, nextP)
#         except Exception as e:
#             common.writeLog("error", "run", json.dumps(e),"amz_shop_log")
#             print("中断...:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), e)
#             run()
def run(key,nhref):
    if key =="":
        keysData = getKeys()
        els = keysData["keys"]
    else:
        els = key
    print(els)
    common.writeLog("tips", "run", "get:"+json.dumps(els),"amz_shop_log")
    # keyId = keysData["id"]
    if els:
        if nhref == "":
            rsp = search(els)
        else:
            rsp = read_next(nhref[0])
        if rsp:
            html = etree.HTML(rsp)
            url = html.xpath(
                '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]/@href')
            try:
                for item in url:
                    inner_rsp = inner_search(item)
                    print("item",inner_rsp)
                    if inner_rsp:
                       infoData = dataDeal(inner_rsp,els)
                       if infoData:
                            updataEvent(infoData)
                nextP = nextPage(html)
                if (len(nextP)):  # 判断是否有下一页
                    common.writeLog("tips", "run", "next page:" + els[0],"amz_shop_log")
                    run(els, nextP)
            except Exception as e:
                common.writeLog("error", "run", json.dumps(e),"amz_shop_log")
                print("中断...:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), e)
                run("","")
        else:
            print("没能搜索到内页数据" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    else:
        print("finish" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

if __name__ == '__main__':   #入口函数
    urllib3.disable_warnings()
    print("begin:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    urlCount = 0  #爬取的url列表
    shopsCount = 0 #shup数组
    # timeToPoint()
    # export_data_to_excel()
    while(True):
        run("","")