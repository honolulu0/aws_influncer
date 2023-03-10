
import datetime
import urllib3
import requests
import json
import random
import pandas as pd
from agents import agents
import common

tagsList = {}
excelList = {'A': ["关键词"], 'B': ["网红"],'C':["链接"],'D':["粉丝量"],'E':["facebook"],'F':["instgram"]}
# 获取关键字
def queryStruct():
    url = "https://ebus-b1.test.api.sui10.com/json/external/queryStruct"
    headers = common.getHeader()
    datas = {"req": {"token": ""}}
    r = requests.post(url,
                     data=json.dumps(datas),
                     headers=headers,
                     # proxies=proxies,
                     verify=False)
    if r.status_code == 200:
        # print(r.text)
        data = json.loads(r.text)
        if data['tars_ret'] == 0:
            tagArr = data["rsp"]["tags"]
            #关键字区分大类
            for item in tagArr:
                if item["class0"] in tagsList:
                    tags = []
                    if item["class0"]:
                        tags.append(item["class0"])
                    else:
                        tags.append("")
                    if item["class1"]:
                        tags.append(item["class1"])
                    else:
                        tags.append("")
                    if item["class2"]:
                        tags.append(item["class2"])
                    else:
                        tags.append("")
                    if tags in tagsList[item["class0"]]:
                        pass
                    else:
                        tagsList[item["class0"]].append(tags)
                else:
                    tagsList[item["class0"]] = []
                    tags = []
                    if item["class0"]:
                        tags.append(item["class0"])
                    else:
                        tags.append("")
                    if item["class1"]:
                        tags.append(item["class1"])
                    else:
                        tags.append("")
                    if item["class2"]:
                        tags.append(item["class2"])
                    else:
                        tags.append("")
                    tagsList[item["class0"]].append(tags)

            for tagsSub in tagsList:
                print(tagsSub)
                if len(tagsList[tagsSub])>0:
                    excelList = {'A': ["关键词"], 'B': ["网红"], 'C': ["链接"],'D': ["链接"], 'E': ["粉丝量"], 'F': ["facebook"],
                                 'G': ["instgram"]}
                    #存储一个大类的数据
                    for classtype in tagsList[tagsSub]:
                        # print(classtype)
                        queryByTag(classtype,excelList)
                    df = pd.DataFrame(excelList)
                    export_data_to_excel(df,classtype[0])
    else:
        # handle_request_err(r.status_code)
        return None
def export_data_to_excel(df,name):    #导出excel
  # encoding编码方式，sheet_name表示要写到的sheet名称， 默认为0， header=None表示不含列名
  df.to_excel("./excel/"+name+".xlsx",  sheet_name="first", header=None)

# 查询当前分类的网红
def queryByTag(classtype,excelList):
    class0 = classtype[0]
    class1=classtype[1]
    class2=classtype[2]
    url = "https://ebus-b1.test.api.sui10.com/json/external/queryByTag"
    headers = common.getHeader()
    datas = {"req": {
        "token": "",
        "tag": {
            "class0":class0,
            "class1":class1,
            "class2":class2
        }
    }}
    r = requests.post(url,
                      data=json.dumps(datas),
                      headers=headers,
                      # proxies=proxies,
                      verify=False)
    if r.status_code == 200:
        # print(r.text)
        data = json.loads(r.text)
        records = data["rsp"]["records"]
        if len(records) > 0:
            influncers  = records[0]["influncers"]
            getQueryProfile(influncers,classtype,excelList)
    else:
        return None

def getQueryProfile(influncers,classtype,excelList):
    url = "https://ebus-b1.test.api.sui10.com/json/external/query_profile"
    headers = common.getHeader()
    datas = {"req": {"token": "","names":influncers}}
    r = requests.post(url,
                      data=json.dumps(datas),
                      headers=headers,
                      # proxies=proxies,
                      verify=False)
    if r.status_code == 200:
        userData = json.loads(r.text)
        profiles = userData["rsp"]["profiles"]
        # excelList = {'A': ["关键词"], 'B': ["网红"], 'C': ["链接"], 'D': ["粉丝量"], 'E': ["facebook"],'F': ["instgram"]}
        if len(profiles)>0:
            for i in profiles:
                if i["subscribes"] > 10000:
                    videoArr = json.loads(i["videos"])
                    if len(videoArr) > 0:
                        if 'viewCountText' in videoArr[0]:
                            viewCountText = videoArr[0]["viewCountText"]
                            ishalfaYear = False
                            if 'year' in viewCountText:
                                pass
                            if 'months' in viewCountText:
                                mon = viewCountText.split(" ")
                                monNum = int(mon[0])
                                if monNum > 0 and monNum < 7:
                                    ishalfaYear = True
                            if 'hours' in viewCountText or 'second' in viewCountText or 'minute' in viewCountText or 'days' in viewCountText or ishalfaYear:
                                excelList['A'].append(classtype[0] + " " + classtype[1] + " " + classtype[2])
                                excelList['B'].append(i["name"])
                                if 'location' in i:
                                    excelList['C'].append(i["location"])
                                else:
                                    excelList['C'].append("")
                                if 'homepage' in i:
                                    excelList['D'].append(i["homepage"])
                                else:
                                    excelList['D'].append("")
                                excelList['E'].append(i["subscribes"])
                                excelList['F'].append(i["facebook"])
                                excelList['G'].append(i["instgram"])
                            else:
                                pass
    else:
        return None

if __name__ == '__main__':
    urllib3.disable_warnings()
    print("begin:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    queryStruct()