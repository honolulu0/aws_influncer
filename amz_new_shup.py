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
import amz_new_shup_config
nowPage = 1
nowIndex = 0
listIndex = 0
rankName = ""
nowUrl = amz_new_shup_config.type[nowIndex]
proxies ={
    'http': "http://127.0.0.1:1087",
    'https': "http://127.0.0.1:1087"
    # 'http': "http://127.0.0.1:58591",
    # 'https': "http://127.0.0.1:58591"
}
def handle_request_err(status_code):
    if status_code == 503:
        print('被反爬虫拦截，休眠30分钟')
        time.sleep(1800)
def handle_random_sleep():
    index = random.randint(0,60)
    time.sleep(index)
def readIndex():
    global nowUrl
    file = r'./' +"amz_new_shup.json"
    global nowIndex,listIndex
    with open(file, 'r') as f:
        # f.write(newContext)
        data = f.read()
        jsonData = json.loads(data)
        if data:
            nowIndex = int(jsonData["nowIndex"])
            listIndex = int(jsonData["listIndex"])
            nowUrl = amz_new_shup_config.type[nowIndex]
def cleanIndex():
    file = r'./' + "amz_new_shup.json"
    with open(file, 'w') as f:
        f.write("")
def writeIndex(index):
    file = r'./' +"amz_new_shup.json"
    with open(file, 'a+') as f:
        data = {
            "listIndex":listIndex,
            "nowIndex":index
        }
        f.write(json.dumps(data))
def rankIngHref(url):
    headers = common.getHeader()
    r = requests.get(url,
                     data=None,
                     headers=headers,
                     proxies=proxies,
                     verify=False)
    # jsonData = json.loads(r.content)
    # print(r.status_code)
    if r.status_code == 200:
        return r.text
    else:
        return None

# def rankIngHref2(url):
#         headers = common.getHeader()
#         r = requests.get(url,
#                          data=None,
#                          headers=headers,
#                          proxies=proxies,
#                          verify=False)
#         # jsonData = json.loads(r.content)
#         print(r.status_code)
#         if r.status_code == 200:
#             return r.text
#         else:
#             return None
def updataEvent(data):
    headers = common.getHeader()
    url = "https://ebus-b1.test.api.sui10.com/json/amz_seller/update"
    jsonData = {
        "req":{
            "token": "",
            "name": data["rankName"],   #分类名称区分
            "data": json.dumps(data)
        }
    }
    r = requests.get(url,
                     data=json.dumps(jsonData),
                     headers=headers,
                     # proxies=proxies,
                     verify=False)
    try:
        if r.status_code == 200:
            print("updataEvent","success")
            common.writeLog("tips", "updataEvent", data["soldName"] + "save success","amz_new_shup_log")
            return r.text
        else:
            print("updataEvent", "err")
            common.writeLog("error", "updataEvent", data["soldName"] + "save fail","amz_new_shup_log")
            handle_request_err(r.status_code)
            return None
    except Exception as e:
        print(e)


def getInfo(url,rankName,rank):
    # url = "https://www.amazon.com/Queen-Size-Sheet-Set-Breathable/dp/B01M16WBW1/ref=zg-bs_home-garden_sccl_2/137-4932335-4056965?pd_rd_w=XS9GC&content-id=amzn1.sym.309d45c5-3eba-4f62-9bb2-0acdcf0662e7&pf_rd_p=309d45c5-3eba-4f62-9bb2-0acdcf0662e7&pf_rd_r=JEMYZD5N2VTVJCFY1237&pd_rd_wg=hWBN2&pd_rd_r=a9c549d3-8f1a-42c7-998e-ced90aaa8347&pd_rd_i=B01M16WBW1&psc=1"
    conent = rankIngHref(url)
    if conent:
        html = etree.HTML(conent)
        view = html.xpath("//span[@id='acrCustomerReviewText']/text()")
        froms = html.xpath("//div[@class='tabular-buybox-text']/div[@class='tabular-buybox-text a-spacing-none']/span[@class='a-size-small tabular-buybox-text-message']/text()")
        moneyArr = html.xpath(
            '//span[@class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"]/span[@class="a-offscreen"]/text()')
        shopName = html.xpath('//a[@id="bylineInfo"]/text()')
        shopHref = html.xpath('//a[@id="bylineInfo"]/@href')
        proInfoth = html.xpath('//th[@class="a-color-secondary a-size-base prodDetSectionEntry"]/text()')
        proInfotd = html.xpath('//td[@class="a-size-base prodDetAttrValue"]/text()')
        soldName = html.xpath('//a[@id="sellerProfileTriggerId"]/text()')
        soldHref = html.xpath('//a[@id="sellerProfileTriggerId"]/@href')
        shopTitle = html.xpath('//span[@id="productTitle"]/text()')
        ASIN = ""
        CountryofOrigin = ""
        dataFirst = ""
        viewNum = "0"
        money = ""
        fromsText = ""
        shopNameText = ""
        shopHrefText = ""
        if(len(view)>0):
            viewNum = (view[0]).split(" ")[0]
        if len(moneyArr)>0:
            money = moneyArr[0]
        if len(froms) >0:
            fromsText = froms[0]
        if len(shopName) > 0:
            shops = shopName[0]
            shopNameText = shops[10:len(shops)-7]
        if len(shopHref):
            shopHrefText = shopHref[0]
        soldNameText = ""
        soldHrefText = ""
        if len(soldName) > 0:
            soldNameText = soldName[0]
        if len(soldHref) > 0:
            soldHrefText = soldHref[0]

        for i in range(len(proInfoth)):
            if (i + 1) <= len(proInfotd):
                if "ASIN" in proInfoth[i]:
                    ASIN = proInfotd[i]
                if "Country of Origin" in proInfoth[i]:
                    print("CountryofOrigin", proInfotd, len(proInfotd), len(proInfoth))
                    CountryofOrigin = proInfotd[i]


                if (i+1) <= len(proInfotd)-1 and  "Date First Available " in proInfoth[i+1]:
                    print("进去2")
                    dataFirst = proInfotd[i]
                if (i + 2) <= len(proInfotd) - 1 and "Date First Available " in proInfoth[i + 2]:
                    print("进去1")
                    dataFirst = proInfotd[i]
        shopTitleText = ""
        if len(shopTitle) > 0:
            shopTitleText = shopTitle[0]
        data = {
            "shopTitle":shopTitleText,
            "soldName": soldNameText,  #店铺名
            "soldHref": soldHrefText,
            "rankName":rankName,   #分类
            "rank":rank,         #排名
            "money":money,      #多少钱
            "viewNum":viewNum,   #评论数
            "fromsText":fromsText,  #发货地址
            "shopNameText":shopNameText, #店铺名字
            "shopHref":shopHrefText,    #店铺链接
            "ASIN":ASIN,
            "CountryofOrigin":CountryofOrigin,  #产品地区
            "dataFirst":dataFirst   #上架时间
        }
        # print(conent)
        # print(data)
        getShopInfo(data)
def getShopInfo(data):
    if data["soldHref"] != "":
        result = parse.urlparse(data["soldHref"])
        query_dict = parse.parse_qs(result.query)
        seller = ""
        if len(query_dict["seller"]) > 0:
            seller = query_dict["seller"][0]
        url = "https://www.amazon.com"+data["soldHref"]
        print(url)
        conent = rankIngHref(url)
        if conent:
            html = etree.HTML(conent)
            linkArr = html.xpath(
                "//div[@id='storefront-link-rd']/span[@class='a-declarative']/a[@class='a-link-normal']/@href")
            AOKETE = html.xpath("//span[@id='seller-contact-button']//span//a/@href")
            business = html.xpath(
                "//div[@id='page-section-detail-seller-info']//div[@class='a-column a-span12 a-spacing-none']//div[@class='a-box a-spacing-none a-color-base-background box-section']//div[@class='a-box-inner a-padding-medium']//div[@class='a-row a-spacing-none']//span/text()")
            businessName = ""
            if len(business) > 1:
                businessName = business[1]
            businessAddress = html.xpath("//div[@class='a-row a-spacing-none indent-left']//span/text()")
            country = ""
            if len(businessAddress) > 0:
                country = businessAddress[len(businessAddress) - 1]

            address = ""
            for a in range(len(businessAddress)):
                if a < len(businessAddress) - 1:
                    address = address + businessAddress[a]
            link = ""

            if len(linkArr) > 0:
                link = "https://www.amazon.com" + linkArr[0]
            data["link"] = link
            data["AOKETE"] = AOKETE[0]
            data["businessName"] = businessName
            data["address"] = address
            data["country"] = country
            data["seller"] = seller
            updataEvent(data)
            # print(data)
    else:
        pass

#商品列表页获取数据
def rankListPage(url):
    global rankName,nowPage,nowIndex,nowUrl,listIndex
    conent = rankIngHref(url)
    if conent:
        listHtml = etree.HTML(conent)
        rankNameArr = listHtml.xpath("//h1[@class='a-size-large a-spacing-medium a-text-bold']/text()")
        if len(rankNameArr) > 0:
            rankName = rankNameArr[0]
            rankName = rankName[16:len(rankName)]
        else:
            rankName = ""
        print("rankName",rankName)
        html = etree.HTML(conent)
        url = html.xpath(
            '//div[@class="p13n-sc-uncoverable-faceout"]/a[@class="a-link-normal"]/@href')
        # print(url)
        rankArr = html.xpath('//span[@class="zg-bdg-text"]/text()')
        # print(rankArr)
        for index,item in enumerate(rankArr):
            if listIndex < index:
                getInfo("https://www.amazon.com"+url[index*2-1],rankName,item)
                listIndex = listIndex +1
                cleanIndex()
                time.sleep(1)
                writeIndex(nowIndex)

        nextData = html.xpath("//div[@class='p13n-desktop-grid']/@data-client-recs-list")
        # print(rankArr)
        # print(nextData)
        if len(nextData) >0:
            nextPageNowP(nextData[0])
        # nextHref = html.xpath("//li[@class='a-last'/a/@href]")
        if nowPage < 8:
            nowPage = nowPage +1
            listIndex = 0
            cleanIndex()
            time.sleep(1)
            writeIndex(nowIndex)
            rankListPage(nowUrl+"?_encoding=UTF8&pg="+str(nowPage))
        else:
            nowPage = 0
            if nowIndex < len(amz_new_shup_config.type)-1:
                nowIndex = nowIndex +1
                cleanIndex()
                time.sleep(1)
                print("这里哈哈哈")
                writeIndex(nowIndex)
                nowUrl = amz_new_shup_config.type[nowIndex]
                rankListPage(nowUrl)

def getHeader2():
        headers = {}
        headers[
            "cookie"] = 'session-id=137-4932335-4056965; i18n-prefs=USD; ubid-main=134-2722039-5371754; lc-main=en_US; x-main="kCpyjovHhV1UMIbmWDUwFrL9zR69fgXuqoigSVOz4@rKboVGlZghXFEaIEwSyS0P"; at-main=Atza|IwEBIPlHBMzDN_5bffbKrWO_7ax0jeIGm4hL-i7R9Vzc-_8jENYfQD6lV3sMbDkBRbZCsICRAFx0KLVaCSNqnpbpsvA_Gb5zs2IWsPR9rS4ej6LNpMDdAZfGiGJiI4DBFkIOuON9B8bJEZiuIgAjHnKwAdRhazFOycyUFbTZ40DqHAFdLURtdczc2_tTK7VznghavMjFYdjx0cdn3CxdPOIPbgA1; sess-at-main="7fKPGJ8UjfHqu/e4l+raKhzZf4J4NbyeVZAHdKslrPs="; sst-main=Sst1|PQGKliatqXWML-Fb3ttsA30HCexY1PUod21YY8UqcA_4Xgv7_VgeCqYC0nMTL4rKWU8PljptBobNgjVV3pqyvC_iRiptjX36ZiYPFpCZ-1QmE1kK8_Iuq--Xws6V2p0p23XgaM2PVrHmWZUMHdjc0r47cWGzaKULbqk6T65XGxlxb3x9jnt-m5F1n7BAnuOgi9M2BnY9cjUGDfamFGlyqy_F34tYNgve8tsMeyHjNrD6g_Ffoj3G9GFDR4txYeCfsminwpepR8m50TIygazAfisXFf_Jykdo8IFNjJUvhCOryds; session-id-time=2082787201l; session-token=aHUk5UMfFYImFADSV16TZBSOsmnR8lysNHMDbugyGm6FL9fbsCT1gFIBXIJgiUFX52K8nJZfgxlENuB1Fj+602//z6thxvrWZn9H28QLauWbgvZI9Im2UMRzkqZObE4gNJMy4jhvAAz2zj19E58Um6EQAuNwCNopyUef4DCehUJlMwAnTKgjokmMW61GBLa/p4kt5m8SeUtWCkrW30ROWx2cp6fDEitMlIf9nvtpE7mxVduKSk6rBBeJYXbQxwkN; csm-hit=tb:s-KNJJKEWDM32D2HVYAPWT|1676280359658&t:1676280360266&adb:adblk_no'

        headers["authority"] = "www.amazon.com"
        headers["accept"] = "text/html, application/json"
        headers["accept-encoding"] = "gzip, deflate, br"
        headers["accept-language"] = "zh-CN,zh;q=0.9"
        headers["content-length"] = "2272"
        headers["content-type"] = "application/json"
        headers["origin"] = "https://www.amazon.com"
        headers["pragma"] = "no-cache"
        headers["referer"] = "https://www.amazon.com/Best-Sellers-Amazon-Devices-Accessories/zgbs/amazon-devices/ref=zg_bs_pg_1?_encoding=UTF8&pg=1"
        headers["x-requested-with"] = "XMLHttpRequest"
        headers["device-memory"] = "8"
        headers["downlink"] = "7.6"
        headers["dpr"] = "1.25"
        headers["ect"] = "4g"
        headers["rtt"] = "100"
        headers["sec-ch-device-memory"] = "8"
        headers["sec-ch-dpr"] = "1.25"
        headers["sec-ch-ua"] = "Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"
        headers["sec-ch-ua-mobile"] = "?0"
        headers["sec-ch-ua-platform"] = "window"
        headers["sec-ch-ua-platform-version"] = "14.0.0"
        headers["sec-ch-viewport-width"] = "1182"
        headers["sec-fetch-dest"] = "empty"
        headers["sec-fetch-mode"] = "cors"
        headers["sec-fetch-site"] = "same-origin"
        headers["viewport-width"] = "1182"
        headers["x-amz-acp-params"] = "tok=lf7atrzr-1CjRpq1OFQfym8ejDhT3jOHdztiWCS4Fxw;ts=1676280358309;rid=KNJJKEWDM32D2HVYAPWT;d1=965;d2=UR"


        headers[
            "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        return headers
def nextPageNowP(dataStr):
    headers = getHeader2()
    datas = json.loads(dataStr)
    ids = []
    indexes = []
    for i,s in enumerate(datas):
        if i > 30:
            indexes.append(i)
            ids.append(json.dumps(s))
    url="https://www.amazon.com/acp/p13n-zg-list-grid-desktop/p13n-zg-list-grid-desktop-af987328-a7e0-4dae-bf81-4982ccdf5e89-1674556762743/nextPage?&stamp=1676276977315"
    data = {"faceoutkataname":"GeneralFaceout",
            "ids":ids,
            "indexes":indexes,
            "linkparameters":"",
            "offset":"31",
            "reftagprefix":"zg_bs_amazon-devices"}
    r = requests.post(url,
                     data=json.dumps(data),
                     headers=headers,
                     # proxies=proxies,
                     verify=False)
    # print(r.status_code)
    if r.status_code == 200:
        # html = etree.HTML(r.text)
        # url = html.xpath(
        #     '//div[@class="p13n-sc-uncoverable-faceout"]/a[@class="a-link-normal"]/@href')
        # print(url)
        # rankArr = html.xpath('//span[@class="zg-bdg-text"]/text()')
        # print(rankArr)
        conent = r.text
        if conent:
            listHtml = etree.HTML(conent)
            rankNameArr = listHtml.xpath("//h1[@class='a-size-large a-spacing-medium a-text-bold']/text()")
            if len(rankNameArr) > 0:
                rankName = rankNameArr[0]
                rankName = rankName[16:len(rankName)]
            else:
                rankName = ""
            html = etree.HTML(conent)
            url = html.xpath(
                '//div[@class="p13n-sc-uncoverable-faceout"]/a[@class="a-link-normal"]/@href')
            # print(url)
            rankArr = html.xpath('//span[@class="zg-bdg-text"]/text()')
            for index, item in enumerate(rankArr):
                getInfo("https://www.amazon.com"+url[index * 2 - 1], rankName, item)

if __name__ == '__main__':   #入口函数
    urllib3.disable_warnings()
    print("begin:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    # while(True):
    readIndex()
    rankListPage(nowUrl)
    # rankIngHref2("https://www.amazon.com/sp?ie=UTF8&seller=A18CBTC7DXCXQJ&asin=B07H7XSP3Y&ref_=dp_merchant_link&isAmazonFulfilled=1")