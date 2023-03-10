import json
import threading
import time


import random

import requests
import datetime
from lxml import etree
from agents import agents

class FileOperate:
    def __init__(self,filepath,filename,way='r',dictData = None,encoding='utf-8'):
        self.filepath = filepath
        self.filename = filename
        self.way = way
        self.dictData = dictData
        self.encoding = encoding
    def operation_file(self):
        if self.dictData:
            self.way = 'w'
            with open(self.filepath+self.filename,self.way,encoding=self.encoding) as f:
                if self.dictData:
                    print(self.dictData)
                    f.write(self.dictData)
    def read_file(self):
        with open(self.filepath+self.filename,self.way,encoding=self.encoding) as f:
            data = f.read()
            print(data)
            return data


def updateSpider(id,influncers):
    now = datetime.datetime.now()
    if len(influncers) > 0:
        printEvent("tips", "updateSpider", "要存储的网红"+json.dumps(influncers))
        headers = getHeader()
        url = 'https://ebus-b1.test.api.sui10.com/json/external/update'
        jsonData = {
            "req":{
                "token":"",
                "id":id,
                "influncers":influncers,
                'timestamp':datetime.datetime.timestamp(now)
            }
        }
        r = requests.get(url,
                         data=json.dumps(jsonData),
                         headers=headers,
                         # proxies=proxies,
                         verify=False)
        # jsonData = json.loads(r.content)
        if r.status_code == 200:
            printEvent("tips", "updateSpider", "网红存储成功")
        else:
            printEvent("error", "updateSpider", "网红存储失败"+json.dumps(influncers))
            return None
    else:
        printEvent("error", "updateSpider", "id没有网红：" +str(id))
        parse_youtube()

def getHeader():

    return dict([('Host', None),
                ('Connection', 'keep-alive'),
                ('Upgrade-Insecure-Requests', '1'),
                ('User-Agent', random.choice(agents)),
                ('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'),
                ('Accept-Language', 'en-US,en;q=0.9'),
                ('Accept-Encoding', 'gzip, deflate')])

proxies ={
    # 'http': "http://127.0.0.1:1087",
    # 'https': "http://127.0.0.1:1087"
    'http': "http://127.0.0.1:58591",
    'https': "http://127.0.0.1:58591"
}
def handle_request_err(status_code):
    if status_code == 503:
        printEvent("warn", "handle_request_err", "被反爬虫拦截，休眠30分钟")
        time.sleep(1800)
def getKeys():   #获取关键字
    headers = getHeader()
    url = 'https://ebus-b1.test.api.sui10.com/json/external/key'
    r = requests.get(url,
                     data='{"req": {"token": "","cid":8}}',
                     headers=headers,
                     # proxies=proxies,
                     verify=False)
    jsonData = json.loads(r.content)
    if r.status_code == 200:
        return jsonData['rsp']
    else:
        return None
def getUserInfo(url):
    headers = getHeader()
    r = requests.get("https://www.youtube.com"+url,
                     data=None,
                     headers=headers,
                     proxies=proxies,
                     verify=False)
    printEvent("tips","getUserInfo",str(r.status_code))
    if r.status_code == 200:
        return r.text
    else:
        handle_request_err(r.status_code)
        return None

def updateProfile(influncer,subscribes,facebook,instgram,videos,location,homepage):  #搜索数据上报（网红详细信息）
    headers = getHeader()
    subscrNum = 0
    if len(subscribes) > 0:
        subscr = subscribes.split(" ")
        if 'K' in subscr[0]:
            subscrNum = int(float(subscr[0][0:len(subscr[0])-1]) * 1000)
        else:
            if 'M' in subscr[0]:
                subscrNum = int(float(subscr[0][0:len(subscr[0])-1]) * 1000000)
            else:
                if 'B' in subscr[0]:
                    subscrNum = int(float(subscr[0][0:len(subscr[0])-1]) * 100000000)
                else:
                    subscrNum = int(subscr[0])
    now = datetime.datetime.now()
    data = {
        "req":{
            "token": "",
            "name": influncer,
            "profile": {
                "name": influncer,
                "subscribes": subscrNum,
                "facebook": facebook,
                "instgram": instgram,
                "videos": videos,
                "timestamp":datetime.datetime.timestamp(now),
                "location":location,
                "homepage":homepage
            }
        }
    }
    url = 'https://ebus-b1.test.api.sui10.com/json/external/update_profile'
    printEvent("tips","updateProfile",json.dumps(data))
    r = requests.get(url,
                     data=json.dumps(data),
                     headers=headers,
                     # proxies=proxies,
                     verify=False)
    # jsonData = json.loads(r.content)
    if r.status_code == 200:
        printEvent("tips","updateProfile",influncer+"录入成功")
        # return jsonData['rsp']
    else:
        printEvent("error", "updateProfile", influncer + "录入失败")
        return None

influncer = []
def parse_youtube():
    page = 1
    keysData = getKeys()
    print("keysData",keysData)
    keys = keysData["keys"]
    keyId = 8
    # keys=["Automotive", "Car", "Care", "Cleaning", "Kits"]
    url = "http://www.youtube.com/results?search_query="
    if len(keys) > 0:
        keysList = keys[0].split(" ")
        for key in keysList:
            url += key + "+"
        url = url[:len(url) - 1]

        printEvent("tips","parse_youtube","请求 parsing youtube url:" + url)
        headers = {'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Connection': 'Keep-Alive',
                   'Host': 'www.youtube.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
        r = requests.get(url,
                         data=None,
                         headers=headers,
                         proxies =proxies,
                         verify=False)
        printEvent("tips","parse_youtube",str(r.status_code))
        if r.status_code == 200:
            try:
                html = etree.HTML(r.text)
                url = html.xpath('//script/text()')
                time.sleep(2)
                jsonString = url[22][20:len(url[22]) - 1]
                if len(jsonString):
                    jsonLoads = json.loads(jsonString)
                    sectionListRenderer = jsonLoads["contents"]['twoColumnSearchResultsRenderer']['primaryContents'][
                            'sectionListRenderer']['contents'][1]
                    if 'continuationItemRenderer' in sectionListRenderer:
                        continuationToken = sectionListRenderer['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
                    else:
                        continuationToken = ""
                    jsonData = \
                        jsonLoads["contents"]['twoColumnSearchResultsRenderer']['primaryContents'][
                            'sectionListRenderer'][
                            'contents'][0]['itemSectionRenderer']['contents']
                    if len(jsonData) > 0:
                        influncer = []
                        for item in jsonData:
                            if 'shelfRenderer' in item:
                                shelfRendererData = item["shelfRenderer"]["content"]["verticalListRenderer"]["items"]
                                for i in shelfRendererData:
                                    if "videoRenderer" in i:
                                        influncer =  getYoutubUser(i,keyId,influncer)
                            if "videoRenderer" in item:
                                influncer = getYoutubUser(item,keyId,influncer)
                        if continuationToken:
                            parse_youtubeTurn(continuationToken,keyId,influncer,page)
                        else:
                            parse_youtube()
                    else:
                        parse_youtube()
            except Exception as e:
                ###解析内层失败的一场处理
                printEvent("error", "parse_youtube", e)

        else:
            parse_youtube()

def parse_youtubeTurn(continuation,keyId,influncer,page):
    headers = getHeader()
    boolType = bool(1)
    boolTypef=bool(0)
    datas = {"context":{"client":{"hl":"zh-CN","gl":"AU","remoteHost":"2a11:3:200:0:0:0:0:403f","deviceMake":"","deviceModel":"","visitorData":"Cgt2NUN5T3JtV010ayiEtpCcBg%3D%3D","userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36,gzip(gfe)","clientName":"WEB","clientVersion":"2.20221122.06.00","osName":"Windows","osVersion":"10.0","originalUrl":"https://www.youtube.com/results?search_query=Automotive+Car+Care+Cleaning+Kits","screenPixelDensity":1,"platform":"DESKTOP","clientFormFactor":"UNKNOWN_FORM_FACTOR","configInfo":{"appInstallData":"CIS2kJwGENSDrgUQ4tSuBRCyiP4SELiLrgUQuNSuBRC-tq4FEIeR_hIQzs-uBRDiua4FEJ6Y_hIQw6GuBRCR-PwSENi-rQU%3D"},"screenDensityFloat":1.25,"timeZone":"Asia/Shanghai","browserName":"Chrome","browserVersion":"107.0.0.0","acceptHeader":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","deviceExperimentId":"ChxOekUzTURnNE5qSXhNVEEyTURReU1EazBNdz09EIS2kJwG","screenWidthPoints":1536,"screenHeightPoints":658,"utcOffsetMinutes":480,"userInterfaceTheme":"USER_INTERFACE_THEME_LIGHT","connectionType":"CONN_CELLULAR_4G","memoryTotalKbytes":"8000000","mainAppWebInfo":{"graftUrl":"https://www.youtube.com/results?search_query=Automotive+Car+Care+Cleaning+Kits","pwaInstallabilityStatus":"PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED","webDisplayMode":"WEB_DISPLAY_MODE_BROWSER","isWebNativeShareAvailable":boolType}},"user":{"lockedSafetyMode":boolTypef},"request":{"useSsl":boolType,"internalExperimentFlags":[],"consistencyTokenJars":[]},"clickTracking":{"clickTrackingParams":"CAAQvGkiEwjty5Sf7M_7AhXNR30KHadtCKU="},"adSignalsInfo":{"params":[{"key":"dt","value":"1669602052822"},{"key":"flash","value":"0"},{"key":"frm","value":"0"},{"key":"u_tz","value":"480"},{"key":"u_his","value":"13"},{"key":"u_h","value":"864"},{"key":"u_w","value":"1536"},{"key":"u_ah","value":"816"},{"key":"u_aw","value":"1536"},{"key":"u_cd","value":"24"},{"key":"bc","value":"31"},{"key":"bih","value":"658"},{"key":"biw","value":"1519"},{"key":"brdim","value":"0,0,0,0,1536,0,1536,816,1536,658"},{"key":"vis","value":"1"},{"key":"wgl","value":"true"},{"key":"ca_type","value":"image"}],"bid":"ANyPxKpX-PF-bd_sSLUYa_hPl2Wjr18Gxp7u5xy-iZiwj9GVBpzMYYqBLUVDRfQdm97YCVQbHIg6B74nCFEYitNLuBVvgHKG9w"}},
             "continuation":continuation}
    curl = "https://www.youtube.com/youtubei/v1/search?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&prettyPrint=false"
    r = requests.post(curl,
                     data=json.dumps(datas),
                     headers=headers,
                     proxies=proxies,
                     verify=False)
    if r.status_code == 200:
        try:
            rspData = json.loads(r.text)
            continuationToken = \
                rspData["onResponseReceivedCommands"][0]["appendContinuationItemsAction"]["continuationItems"][1][
                    "continuationItemRenderer"]["continuationEndpoint"]["continuationCommand"]["token"]
            jsonData = \
            rspData["onResponseReceivedCommands"][0]["appendContinuationItemsAction"]["continuationItems"][0][
                "itemSectionRenderer"]["contents"]
            for item in jsonData:
                if 'shelfRenderer' in item:
                    shelfRendererData = item["shelfRenderer"]["content"]["verticalListRenderer"]["items"]
                    for i in shelfRendererData:
                        if "videoRenderer" in i:
                            getYoutubUser(i, keyId, influncer)
                if "videoRenderer" in item:
                    getYoutubUser(item, keyId, influncer)
            if continuationToken:
                printEvent("tips","parse_youtubeTurn","continuationToken存在时下一页")
                nowPage = page + 1
                if nowPage == 11:
                    parse_youtube()
                else:
                    parse_youtubeTurn(continuationToken, keyId, influncer,nowPage)
            else:
                parse_youtube()
        except Exception as e:
            printEvent("error","parse_youtubeTurn",e)
            parse_youtube()

def printEvent(type,clue,info):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')+"|"+type+"|"+clue+"|:",info)
def writeLog(type,clue,key):
    if type == "success":
        oldContext = FileOperate(dictData="", filepath='./log/', filename='youtub_success.log').read_file()
        newContext = oldContext+(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')+"|"+type+"|"+clue+"|:"+key)+",\n"
        FileOperate(dictData=newContext, filepath='./log/', filename='youtub_success.log').operation_file()
    if type == "error":
        oldContext = FileOperate(dictData="", filepath='./log/', filename='youtub_error.log').read_file()
        newContext = oldContext + (datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S.%f') + "|" + type + "|" + clue + "|:" + key) + ",\n"
        FileOperate(dictData=newContext, filepath='./log/', filename='youtub_error.log').operation_file()

def getYoutubUser(item,keyId,influncer):
    try:
        name = item["videoRenderer"]["ownerText"]["runs"][0]["text"]
        if name in influncer:
            pass
        else:
            influncer.append(name)
        canonicalBaseUrl = \
            item["videoRenderer"]["ownerText"]["runs"][0]["navigationEndpoint"][
                "browseEndpoint"][
                "canonicalBaseUrl"]
        # //https://www.youtube.com/@JwettManD/videos
        datas = getUserInfo(canonicalBaseUrl + "/videos")
        aboutDatas = getUserInfo(canonicalBaseUrl + "/about")
        faceBook = ""
        instagram = ""
        videoList = []
        location = ""
        homepage=""

        aboutHtml = etree.HTML(aboutDatas)
        aboutText = aboutHtml.xpath('//script/text()')
        if aboutText and len(aboutText) >= 23:
            aboutJsonString = aboutText[23][20:len(aboutText[23]) - 1]
            userJsonData = json.loads(aboutJsonString)
            aboutTabs = userJsonData["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]
            homepage = userJsonData["metadata"]["channelMetadataRenderer"]["vanityChannelUrl"]
            for item in aboutTabs:
                if ("tabRenderer" in item) and item["tabRenderer"]["title"] == "About":
                    sectionListRenderer = item["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
                    if len(sectionListRenderer) > 0:
                        if "country" in sectionListRenderer[0]["itemSectionRenderer"]["contents"][0]["channelAboutFullMetadataRenderer"]:
                                location = sectionListRenderer[0]["itemSectionRenderer"]["contents"][0][
                                    "channelAboutFullMetadataRenderer"]["country"]["simpleText"]

        html = etree.HTML(datas)
        text = html.xpath('//script/text()')

        if text and len(text) >= 23:
            userJsonString = text[23][20:len(text[23]) - 1]
            userJsonData = json.loads(userJsonString)
            # 获取用户名字
            userName = userJsonData["header"]["c4TabbedHeaderRenderer"]["title"]
            simpleText = \
                userJsonData["header"]["c4TabbedHeaderRenderer"]["subscriberCountText"][
                    "simpleText"]

            if "headerLinks" in userJsonData["header"][
                "c4TabbedHeaderRenderer"] and "secondaryLinks" in \
                    userJsonData["header"]["c4TabbedHeaderRenderer"]["headerLinks"][
                        "channelHeaderLinksRenderer"]:
                secondaryLinks = \
                    userJsonData["header"]["c4TabbedHeaderRenderer"]["headerLinks"][
                        "channelHeaderLinksRenderer"]["secondaryLinks"]
                # 当secondaryLinks里面没有要的数据的时候看看primaryLinks里面有没有
                for item in secondaryLinks:  # 获取用户联系方式
                    if item["title"]["simpleText"] == "Facebook":
                        faceBook = item["navigationEndpoint"]["urlEndpoint"]["url"]
                    if item["title"]["simpleText"] == "Instagram":
                        instagram = item["navigationEndpoint"]["urlEndpoint"]["url"]
                if "primaryLinks" in userJsonData["header"]["c4TabbedHeaderRenderer"]["headerLinks"][
                    "channelHeaderLinksRenderer"]:
                    primaryLinks = \
                        userJsonData["header"]["c4TabbedHeaderRenderer"]["headerLinks"][
                            "channelHeaderLinksRenderer"]["primaryLinks"]
                    for itemp in primaryLinks:
                        if itemp["title"]["simpleText"] == "Facebook":
                            faceBook = itemp["navigationEndpoint"]["urlEndpoint"]["url"]
                        if itemp["title"]["simpleText"] == "Instagram":
                            instagram = itemp["navigationEndpoint"]["urlEndpoint"]["url"]
                userTabs = userJsonData["contents"]["twoColumnBrowseResultsRenderer"]["tabs"]

                for item in userTabs:  # 获取前十播放量和时间
                    if ("tabRenderer" in item) and item["tabRenderer"]["title"] == "Videos":
                        videoData = item["tabRenderer"]["content"]["richGridRenderer"][
                            "contents"]
                        dataLen = len(videoData)
                        if dataLen > 10:
                            dataLen = 10
                        for vItem in range(dataLen):
                            viewCountText = \
                                videoData[vItem]["richItemRenderer"]["content"][
                                    "videoRenderer"][
                                    "viewCountText"][
                                    "simpleText"]
                            publishedTimeText = \
                                videoData[vItem]["richItemRenderer"]["content"][
                                    "videoRenderer"][
                                    "publishedTimeText"]['simpleText']
                            videoUrl = \
                                videoData[vItem]["richItemRenderer"]["content"][
                                    "videoRenderer"][
                                    "videoId"]
                            videoList.append({
                                'url': 'https://www.youtube.com/watch?v=' + videoUrl,
                                'plays': viewCountText,
                                'viewCountText': publishedTimeText,
                                "canonicalBaseUrl": canonicalBaseUrl
                            })

            # 存储
            updateProfile(userName, simpleText, faceBook, instagram, json.dumps(videoList),location,homepage)
            # 存储关键词网红列表
            updateSpider(keyId, influncer)
            return influncer
    except Exception as e:
        printEvent("error", "getYoutubUser", e)
        parse_youtube()



if __name__ == '__main__':   #入口函数
    print("begin:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

    while(True):
        parse_youtube()
        index = random.randint(0, 60)
        time.sleep(index)
        print("end")

