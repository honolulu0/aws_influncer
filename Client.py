import socket
import threading
import sys
import os
import time
import json
import random
import requests
import datetime
from lxml import etree
from agents import agents
import common

timeOutTimes = 3
nowDate = datetime.datetime.now().strftime('%Y-%m-%d')
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


proxies ={
    'http': "http://127.0.0.1:1087",
    'https': "http://127.0.0.1:1087"
    # 'http': "http://127.0.0.1:58591",
    # 'https': "http://127.0.0.1:58591"
}

influncer = []
def getUserInfo(url,keyId):
    headers = common.getHeader()
    global timeOutTimes
    try:
        r = requests.get("https://www.youtube.com"+url,
                         data=None,
                         headers=headers,
                         proxies=proxies,
                         verify=False,
                         timeout=30)
        printEvent("tips","getUserInfo",str(r.status_code))
        timeOutTimes = 3
        if r.status_code == 200:
            return r.text
        else:
            printEvent("error", "getUserInfo", r.status_code)
            logInfo = {"id": keyId, "error": r.status_code}
            common.writeLog("error", "getUserInfo", json.dumps(logInfo),"youtub_log")
            return None
    except Exception as e:
        logInfo = {"id": keyId, "error": e}
        common.writeLog("error", "getUserInfo", json.dumps(logInfo),"youtub_log")
        if timeOutTimes > 0:
            timeOutTimes =timeOutTimes -1
            getUserInfo(url,keyId)
        else:
            timeOutTimes = 3

def parse_youtubeTurn(continuation,keyId,influncer,page,keys):
    global timeOutTimes
    headers = common.getHeader()
    boolType = bool(1)
    boolTypef=bool(0)
    datas = {"context":{"client":{"hl":"zh-CN","gl":"AU","remoteHost":"2a11:3:200:0:0:0:0:403f","deviceMake":"","deviceModel":"","visitorData":"Cgt2NUN5T3JtV010ayiEtpCcBg%3D%3D","userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36,gzip(gfe)","clientName":"WEB","clientVersion":"2.20221122.06.00","osName":"Windows","osVersion":"10.0","originalUrl":"https://www.youtube.com/results?search_query=Automotive+Car+Care+Cleaning+Kits","screenPixelDensity":1,"platform":"DESKTOP","clientFormFactor":"UNKNOWN_FORM_FACTOR","configInfo":{"appInstallData":"CIS2kJwGENSDrgUQ4tSuBRCyiP4SELiLrgUQuNSuBRC-tq4FEIeR_hIQzs-uBRDiua4FEJ6Y_hIQw6GuBRCR-PwSENi-rQU%3D"},"screenDensityFloat":1.25,"timeZone":"Asia/Shanghai","browserName":"Chrome","browserVersion":"107.0.0.0","acceptHeader":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","deviceExperimentId":"ChxOekUzTURnNE5qSXhNVEEyTURReU1EazBNdz09EIS2kJwG","screenWidthPoints":1536,"screenHeightPoints":658,"utcOffsetMinutes":480,"userInterfaceTheme":"USER_INTERFACE_THEME_LIGHT","connectionType":"CONN_CELLULAR_4G","memoryTotalKbytes":"8000000","mainAppWebInfo":{"graftUrl":"https://www.youtube.com/results?search_query=Automotive+Car+Care+Cleaning+Kits","pwaInstallabilityStatus":"PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED","webDisplayMode":"WEB_DISPLAY_MODE_BROWSER","isWebNativeShareAvailable":boolType}},"user":{"lockedSafetyMode":boolTypef},"request":{"useSsl":boolType,"internalExperimentFlags":[],"consistencyTokenJars":[]},"clickTracking":{"clickTrackingParams":"CAAQvGkiEwjty5Sf7M_7AhXNR30KHadtCKU="},"adSignalsInfo":{"params":[{"key":"dt","value":"1669602052822"},{"key":"flash","value":"0"},{"key":"frm","value":"0"},{"key":"u_tz","value":"480"},{"key":"u_his","value":"13"},{"key":"u_h","value":"864"},{"key":"u_w","value":"1536"},{"key":"u_ah","value":"816"},{"key":"u_aw","value":"1536"},{"key":"u_cd","value":"24"},{"key":"bc","value":"31"},{"key":"bih","value":"658"},{"key":"biw","value":"1519"},{"key":"brdim","value":"0,0,0,0,1536,0,1536,816,1536,658"},{"key":"vis","value":"1"},{"key":"wgl","value":"true"},{"key":"ca_type","value":"image"}],"bid":"ANyPxKpX-PF-bd_sSLUYa_hPl2Wjr18Gxp7u5xy-iZiwj9GVBpzMYYqBLUVDRfQdm97YCVQbHIg6B74nCFEYitNLuBVvgHKG9w"}},
             "continuation":continuation}
    curl = "https://www.youtube.com/youtubei/v1/search?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8&prettyPrint=false"
    r = requests.post(curl,
                     data=json.dumps(datas),
                     headers=headers,
                     proxies=proxies,
                     verify=False,
                     timeout=30)
    timeOutTimes = 3
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
                print("itemssss",item)
                if 'shelfRenderer' in item:
                    shelfRendererData = item["shelfRenderer"]["content"]["verticalListRenderer"]["items"]
                    for i in shelfRendererData:
                        if "videoRenderer" in i:
                            getYoutubUser(i, keyId, influncer,keys)
                if "videoRenderer" in item:

                    getYoutubUser(item, keyId, influncer,keys)
            print("continuationToken",continuationToken)
            if continuationToken:
                printEvent("tips","parse_youtubeTurn","continuationToken存在时下一页")
                nowPage = page + 1
                if nowPage >= 11:
                    pass
                else:
                    parse_youtubeTurn(continuationToken, keyId, influncer,nowPage,keys)
            else:
                pass
        except Exception as e:
            printEvent("error","parse_youtubeTurn",e)
            logInfo = {"id": keyId, "keys": keys, "error": str(e)}
            common.writeLog("error", "parse_youtubeTurn", json.dumps(logInfo),"youtub_log")
            if timeOutTimes > 0:
                timeOutTimes = timeOutTimes - 1
                parse_youtubeTurn(continuation,keyId,influncer,page,keys)
            else:
                timeOutTimes = 3

def browse_youtub(keyId,text,page,keys):  #浏览搜索页面
    try:
        html = etree.HTML(text)
        url = html.xpath('//script/text()')
        time.sleep(2)
        jsonString = url[22][20:len(url[22]) - 1]
        print("len(jsonString)",len(jsonString))
        if len(jsonString):
            jsonLoads = json.loads(jsonString)
            sectionListRenderer = jsonLoads["contents"]['twoColumnSearchResultsRenderer']['primaryContents'][
                'sectionListRenderer']['contents'][1]
            if 'continuationItemRenderer' in sectionListRenderer:
                continuationToken = \
                    sectionListRenderer['continuationItemRenderer']['continuationEndpoint']['continuationCommand'][
                        'token']
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
                                influncer = getYoutubUser(i, keyId, influncer,keys)
                    if "videoRenderer" in item:
                        influncer = getYoutubUser(item, keyId, influncer,keys)
                        print("influncerss",influncer)
                if continuationToken:  # 是否有下一页
                    parse_youtubeTurn(continuationToken, keyId, influncer, page,keys)
    except Exception as e:
        ###解析内层失败的一场处理
        print("keys",keys)
        printEvent("error", "browse_youtub", e)
        logInfo = {"keys": keys, "error": str(e)}
        common.writeLog("error", "browse_youtub", json.dumps(logInfo),"youtub_log")


def parse_youtube(id,keys):
    global timeOutTimes
    try:
        page = 1
        url = "http://www.youtube.com/results?search_query="
        print("keys",keys)
        keysList = keys["keyword"].split(" ")
        for key in keysList:
            url += key + "+"
        url = url[:len(url) - 1]
        printEvent("tips", "parse_youtube", "请求 parsing youtube url:" + url)
        headers = {'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Connection': 'Keep-Alive',
                   'Host': 'www.youtube.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
        r = requests.get(url,
                         data=None,
                         headers=headers,
                         proxies=proxies,
                         verify=False,
                         timeout=30)
        timeOutTimes = 3
        if r.status_code == 200:
            browse_youtub(id,r.text,page,keys)
        else:
            # 返回值不是200
            logInfo = {"id": id, "keys": keys, "error": r.status_code}
            common.writeLog("error", "parse_youtube", json.dumps(logInfo),"youtub_log")
    except Exception as e:
        common.writeLog("error", "parse_youtube", str(e),"youtub_log")
        if timeOutTimes > 0:
            timeOutTimes = timeOutTimes - 1
            parse_youtube(id,keys)
        else:
            timeOutTimes = 3

def getAbout(canonicalBaseUrl,keyId):
    location=""
    aboutDatas = getUserInfo(canonicalBaseUrl + "/about",keyId)
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
                    if "country" in sectionListRenderer[0]["itemSectionRenderer"]["contents"][0][
                        "channelAboutFullMetadataRenderer"]:
                        location = sectionListRenderer[0]["itemSectionRenderer"]["contents"][0][
                            "channelAboutFullMetadataRenderer"]["country"]["simpleText"]
    return {"location":location,"homepage":homepage}
def getYoutubUser(item,keyId,influncer,keys):
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
        # canonicalBaseUrl = "/@JwettManD"
        datas = getUserInfo(canonicalBaseUrl + "/videos",keyId)
        faceBook = ""
        instagram = ""
        videoList = []
        abouts = getAbout(canonicalBaseUrl,keyId)
        location = abouts["location"]
        homepage=abouts["homepage"]
        html = etree.HTML(datas)
        text = html.xpath('//script/text()')
        if text and len(text) >= 23:
            userJsonString = text[23][20:len(text[23]) - 1]
            userJsonData = json.loads(userJsonString)
            # 获取用户名字
            userName = userJsonData["header"]["c4TabbedHeaderRenderer"]["title"]
            classList = queryProfile([userName])
            global saveAble
            saveAble = False
            if classList["class0"] != 0 and classList["tag0"] != 0:
                if classList["class0"] !=keyId:
                    if classList["class1"] != 0 and classList["tag1"] != 0:
                        if classList["class1"] != keyId:
                            if classList["class2"] != 0 and classList["tag2"] != 0:
                                saveAble = True
                            else:
                                saveAble = True
                                classList["class2"] = keyId
                                classList["tag2"] = keys["tid"]
                        else:#keyId == class1
                            saveAble = True
                    else:
                        saveAble = True
                        classList["class1"] = keyId
                        classList["tag1"] = keys["tid"]
                else: #keyId == class0
                    saveAble = True

            else:
                saveAble = True
                classList["class0"]=keyId
                classList["tag0"] = keys["tid"]
            if saveAble == True:
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
                updateProfile(userName, simpleText, faceBook, instagram, json.dumps(videoList),location,homepage,classList)
            return influncer
    except Exception as e:
        printEvent("error", "getYoutubUser", e)
        logInfo = {"id": keyId, "keys": keys, "error": e}
        common.writeLog("error", "getYoutubUser", json.dumps(logInfo),"youtub_log")

def queryProfile(names):
    url = "https://ebus-b1.test.api.sui10.com/json/external/query_profile"
    headers = common.getHeader()
    data = {"req": {"token": "", "names": names}}
    r = requests.post(url,
                     data=json.dumps(data),
                     headers=headers,
                     proxies=proxies,
                     verify=False,
                    timeout=5)
    printEvent("tips", "getUserInfo", str(r.status_code))
    if r.status_code == 200:
        jsonData = json.loads(r.text)
        if jsonData["tars_ret"] == 0:
            profiles = jsonData["rsp"]["profiles"]
            classList = {
                "class0": 0,
                "class1": 0,
                "class2": 0,
                "tag0":0,
                "tag1":0,
                "tag2":0
            }
            if len(profiles) > 0:
                class0 = 0
                class1 = 0
                class2 = 0
                tag0 = 0
                tag1 = 0
                tag2 = 0
                if "class0" in profiles[0]:
                    class0 = profiles[0]["class0"]
                if "class1" in profiles[0]:
                    class1 = profiles[0]["class1"]
                if "class2" in profiles[0]:
                    class2 = profiles[0]["class2"]
                if "tag0" in profiles[0]:
                    tag0 = profiles[0]["tag0"]
                if "tag1" in profiles[0]:
                    tag1 = profiles[0]["tag1"]
                if "tag2" in profiles[0]:
                    tag2 = profiles[0]["tag2"]

                classList["class0"]=class0
                classList["class1"]=class1
                classList["class2"]=class2
                classList["tag0"] = tag0
                classList["tag1"] = tag1
                classList["tag2"] = tag2

            return classList

def printEvent(type,clue,info):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')+"|"+type+"|"+clue+"|:",info)
def updateProfile(influncer,subscribes,facebook,instgram,videos,location,homepage,classList):  #搜索数据上报（网红详细信息）
    headers = common.getHeader()
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
                "class0":classList["class0"],
                "class1":classList["class1"],
                "class2":classList["class2"],
                "tag0":classList["tag0"],
                "tag1":classList["tag1"],
                "tag2":classList["tag2"],
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
    print(data)
    url = 'https://ebus-b1.test.api.sui10.com/json/external/update_profile'
    printEvent("tips","updateProfile",json.dumps(data))
    r = requests.get(url,
                     data=json.dumps(data),
                     headers=headers,
                     # proxies=proxies,
                     verify=False,
                     timeout=5)
    # jsonData = json.loads(r.content)
    if r.status_code == 200:
        printEvent("tips","updateProfile",influncer+"录入成功")
        common.writeLog("tips", "updateProfile", json.dumps(influncer)+"save success","youtub_log")
        # return jsonData['rsp']
    else:
        printEvent("error", "updateProfile", influncer + "录入失败")
        common.writeLog("tips", "updateProfile", json.dumps(influncer) + "save fail","youtub_log")
        return None

def handle_random_sleep():
    index = random.randint(0,10)
    time.sleep(index)


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
                        logInfo = {"id": keyId,"key":ki["keyword"],"tid":ki["tid"]}
                        common.writeLog("success", "receive", json.dumps(logInfo),"youtub_log")
                        parse_youtube(keyId,ki)
                else:
                    logInfo = {"id": keyId, "keys": keys,"tid":0}
                    common.writeLog("success", "receive", json.dumps(logInfo),"youtub_log")
                socket.close()
                sys.exit(0)
        except Exception as e:
            print("服务端已主动断开链接")
            sys.exit(0)
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
    # parse_youtube(1,['men outfit', 'men trends', 'men haul', 'men looks', 'men wardrobe', 'women outfit'])
    # queryProfile(["aaa"])
    # parse_youtube(8,{"tid":1,"keyword":"men outfit"})
    # parse_youtube(8,{"tid": 828, "keyword": "Foundation/make up base favourites"})
    # print("finishsss")
    main()