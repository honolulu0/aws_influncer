import datetime
import time
import urllib3
import requests
import json
import random
import pandas as pd
from agents import agents
from functools import reduce
# https://www.mingdao.com/api/Worksheet/GetFilterRows  获取列表
# https://www.mingdao.com/api/Worksheet/GetRowDetail 拿到projectId
#查询对应的网红详情
#https://www.mingdao.com/api/Worksheet/UpdateWorksheetRow  更新
worksheetId = "6238107f5c0cd73ba25b1034"
appId = "69a6a9e9-7b09-45f7-9e91-8e4f98592259"
viewId = "6238107f5c0cd73ba25b1038"
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


def getHeader():
    headers = {}
    headers[
        "cookie"] = "_ga=GA1.2.839356809.1670468456; Hm_lvt_5763e499eacd42ac563739be7c43ffc7=1670594100,1670633929,1670805245,1670978517; _gid=GA1.2.1486065427.1671153836; md_pss_id=09c0330010180510f303c06f02905700106b0c608a0670bd; Hm_lpvt_5763e499eacd42ac563739be7c43ffc7=1671155836; _gat=1"
    headers["authority"] = "www.mingdao.com"
    headers["accept"] = "application/json, text/javascript, */*; q=0.01"
    headers["accept-encoding"] = "gzip, deflate, br"
    headers["accept-language"] = "zh-CN,zh;q=0.9"
    headers["accountid"] = "2ca1a072-7815-430d-accc-046a14fdd6ce"
    headers["authorization"] = "md_pss_id 0b20ce00808c09702a0d803101a0980aa0f10fc0490290da"
    headers["cache-control"] = "no-cache"
    headers["content-length"] = "251"
    headers["content-type"] = "application/json"
    headers["origin"] = "www.mingdao.com"
    headers["pragma"] = "no-cache"
    headers["referer"] = "https://mingdao.com/"
    headers["x-requested-with"] = "XMLHttpRequest"
    headers[
        "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    return headers
influncersList = {}
pageIndex = 1
def getDataList():
    url = "https://ebus-b1.test.api.sui10.com/json/amazon/query"
    headers = getHeader()
    datas = {"req": {"token": ""}}
    r = requests.post(url,
                      data=json.dumps(datas),
                      headers=headers,
                      # proxies=proxies,
                      verify=False)
    if r.status_code == 200:
        # print(r.text)
        jsonData = json.loads(r.text)
        if jsonData["tars_ret"] == 0:
            records = jsonData["rsp"]["records"]
            if len(records) > 0:
                for a in records:
                    influncers = a["influncers"]
                    if len(influncers) > 0:
                        global influncersList
                        for item in influncers:
                            # print("aaa", item)
                            userNameArr = item.split("##&*%$#")
                            if len(userNameArr) == 2:
                                userName = userNameArr[1]
                            else:
                                userName = userNameArr[0]
                            if userName in influncersList:
                                influncersList[userName].append({"class0":a["class0"],"class1":a["class1"],"class2":a["class2"]})
                            else:
                                influncersList[userName] = [{"class0":a["class0"],"class1":a["class1"],"class2":a["class2"]}]
            getFilterRows()
    else:
        return None

def handle_random_sleep():
    time.sleep(3)


#worksheetId
#appId
#viewId 固定
#获取列表
def getFilterRows():
    try:
        global pageIndex
        url = "https://www.mingdao.com/api/Worksheet/GetFilterRows"
        headers = getHeader()
        datas = {
            "worksheetId": worksheetId,
            "pageSize": 50,
            "pageIndex": pageIndex,
            "status": 1,
            "appId": appId,
            "viewId": viewId,
            "searchType": 1,
            "keyWords": "",
            "filterControls": [], "fastFilters": [], "navGroupFilters": []
        }
        r = requests.post(url,
                          data=json.dumps(datas),
                          headers=headers,
                          # proxies=proxies,
                          verify=False)
        printEvent("tips", "getFilterRows", r.status_code)
        if r.status_code == 200:
            jsonData = json.loads(r.text)
            wsData = jsonData["data"]["data"]
            if len(wsData) > 0:
                for item in wsData:
                    rowid = item["rowid"]
                    getRowDetail(rowid)
                pageIndex = pageIndex +1
                getFilterRows()
            else:
                printEvent("tips", "getFilterRows", "ended")
                writeLog("tips", "getFilterRows", "ended")
        else:
            return None
    except Exception as e:
        printEvent("error", "getFilterRows", e)
        printEvent("error", "getFilterRows", "如果显示'data'应该是没登录")
        writeLog("error", "getFilterRows", "no'data'no login")

#获取projectId
def getRowDetail(rowId):
    try:
        url = "https://www.mingdao.com/api/Worksheet/GetRowDetail"
        headers = getHeader()
        handle_random_sleep()
        datas = {
            "worksheetId": worksheetId,
            "rowId": rowId,
            "getType": 1,
            "appId": appId,
            "viewId": viewId,
            "checkView": True,
            "getTemplate": True
        }
        r = requests.post(url,
                          data=json.dumps(datas),
                          headers=headers,
                          # proxies=proxies,
                          verify=False)
        printEvent("tips", "getRowDetail", r.status_code)
        if r.status_code == 200:
            jsonData = json.loads(r.text)
            projectId = jsonData["data"]["projectId"]
            rowDataStr = json.loads(jsonData["data"]["rowData"])
            for a in rowDataStr:
                infoObj = is_json(rowDataStr[a])
                isNum = is_numbers(infoObj)
                if isNum == False and len(infoObj) > 0:
                    for key in infoObj:
                        if 'name' in key:
                            print("namess",key["name"])
                            print("isIn", key["name"] in influncersList)
                            if key["name"] in influncersList and len(influncersList[key["name"]]) > 0:
                                inputInfluncersList = reduce(lambda x,y:x+[y] if y not in x else x,[[],]+influncersList[key["name"]])
                                print("inputInfluncersList",inputInfluncersList)
                                UpdateWorksheetRow(projectId, rowId,inputInfluncersList,key["name"])

        else:
            return None
    except Exception as e:
        printEvent("error", "getRowDetail", e)
        writeLog("error", "getRowDetail", str(e))

def is_numbers(s):
    try:
        float(s)
        return True
    except Exception as e:
        return False

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
        return json_object
    except Exception as e:
        return []

def UpdateWorksheetRow(projectId,rowId,classList,name):
    class01 = ""
    class02 = ""
    class03 = ""
    class11 = ""
    class12 = ""
    class13 = ""
    class21 = ""
    class22 = ""
    class23 = ""
    if len(classList) > 0:
        class01 = classList[0]["class0"]
        class02 = classList[0]["class1"]
        class03 = classList[0]["class2"]
    if len(classList) > 1:
        class11 = classList[1]["class0"]
        class12 = classList[1]["class1"]
        class13 = classList[1]["class2"]
    if len(classList) >2:
        class21 = classList[2]["class0"]
        class22 = classList[2]["class1"]
        class23 = classList[2]["class2"]
    url = "https://www.mingdao.com/api/Worksheet/UpdateWorksheetRow"
    headers = getHeader()
    datas = {
        "appId":appId,
        "viewId":viewId,
        "getType":1,
        "worksheetId":worksheetId,
        "rowId":rowId,
        "newOldControl":[
            {"controlId":"639c2d6d6f0889b5c66aa9d4","type":2,"value":class01,"controlName":"种类1一级分类","dot":0},
            {"controlId":"639c2d6d6f0889b5c66aa9d5","type":2,"value":class02,"controlName":"种类1二级分类","dot":0},
            {"controlId":"639c2d6d6f0889b5c66aa9d6","type":2,"value":class03,"controlName":"种类1三级分类","dot":0},
            {"controlId":"639c2d6d6f0889b5c66aa9d7","type":2,"value":class11,"controlName":"种类2一级分类","dot":0},
            {"controlId":"639c2d6d6f0889b5c66aa9d8","type":2,"value":class12,"controlName":"种类2二级分类","dot":0},
            {"controlId":"639c2d6d6f0889b5c66aa9d9","type":2,"value":class13,"controlName":"种类2三级分类","dot":0},
            {"controlId":"639c2d6d6f0889b5c66aa9da","type":2,"value":class21,"controlName":"种类3一级分类","dot":0},
            {"controlId":"639c2d6d6f0889b5c66aa9db","type":2,"value":class22,"controlName":"种类3二级分类","dot":0},
            {"controlId":"639c2d6d6f0889b5c66aa9dc","type":2,"value":class23,"controlName":"种类3三级分类","dot":0}
        ],
        "projectID":projectId
    }
    r = requests.post(url,
                      data=json.dumps(datas),
                      headers=headers,
                      # proxies=proxies,
                      verify=False)
    printEvent("tips", "UpdateWorksheetRow", r.status_code)
    if r.status_code == 200:
        jsonData = json.loads(r.text)
        if jsonData["state"] == 1 and jsonData["data"]["resultCode"] == 1:
            printEvent("tips", "UpdateWorksheetRow", "更新成功:"+name)
            writeLog("tips", "UpdateWorksheetRow", "save success:"+name)
        else:
            printEvent("warn", "UpdateWorksheetRow", "更新失败:"+name)
            writeLog("warn", "UpdateWorksheetRow", "save fail:"+name)
    else:
        return None

def printEvent(type,clue,info):
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')+"|"+type+"|"+clue+"|:",info)
def writeLog(type,clue,key):
    # oldContext = FileOperate(dictData="", filepath='./log/', filename='mingdaoyun_amz_log.log').read_file()
    newContext = (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')+"|"+type+"|"+clue+"|:"+key)+",\n"
    # FileOperate(dictData=newContext, filepath='./log/', filename='mingdaoyun_amz_log.log').operation_file()
    file = r'./log/mingdaoyun_amz_log_'+nowDate+'.log'
    with open(file, 'a+') as f:
        f.write(newContext)

if __name__ == '__main__':
    urllib3.disable_warnings()
    print("begin:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    # getFilterRows(pageIndex)
    getDataList()