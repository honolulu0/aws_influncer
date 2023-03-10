import json
import sys
import threading
import time
import random

import requests
import datetime

import urllib3
import common
import amz_seller_massag_config
from lxml import etree
from agents import agents
from bs import bs
from urllib import parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver .common .by import By

marketplaceID = ""
sellerID = ""
begins = 0
myIndex = 0
loginTime = 0
loginIndex = 0
isStart = False
excelList = {'A': ["发信时间"], 'B': ["用户账号"],'C':["第几个"],'D':["url"],'E':["shop"],'F':["ASIN"],'G':["seller"]}
times = ""
nowHelloIndex = 0
helloArr=[
    "Hi，Amazon Seller.",
    "Hello, Amazon Seller.",
    "Howdy , Amazon Seller.",
    "How are you? Amazon Seller.",
    "What's up? Amazon Seller .",
    "Nice to meet to，Amazon Seller."
]
def getTimes():
    global times,excelList
    excelList = {'A': ["发信时间"], 'B': ["用户账号"],'C':["第几个"],'D':["url"],'E':["shop"],'F':["ASIN"],'G':["seller"]}
    times = datetime.datetime.now().strftime('%Y-%m-%d')+"-"+datetime.datetime.now().strftime('%H-%M-%S')


def handle_request_err(status_code):
    if status_code == 503:
        print('被反爬虫拦截，休眠30分钟')
        time.sleep(1800)
def handle_random_sleep():
    index = random.randint(0,60)
    time.sleep(index)
def readIndex():
    file = r'./' +"amz_send.json"
    with open(file, 'r') as f:
        # f.write(newContext)
        data = f.read()
        wirteData = "1"
        if data:
            wirteData = data
        print(wirteData)
        return int(wirteData)
def cleanIndex():
    file = r'./' + "amz_send.json"
    with open(file, 'w') as f:
        f.write("")
def writeIndex(index):
    file = r'./' +"amz_send.json"
    with open(file, 'a+') as f:
        f.write(str(index+1))
def readIndexUser():
    global loginTime,loginIndex
    file = r'./' +"amz_send_user.json"
    with open(file, 'r') as f:
        # f.write(newContext)
        data = f.read()
        if data:
            wirteData = json.loads(data)
            loginTime = wirteData["loginTime"]
            loginIndex =  wirteData["loginIndex"]

def cleanIndexUser():
    file = r'./' + "amz_send_user.json"
    with open(file, 'w') as f:
        f.write("")
def writeIndexUser():
    file = r'./' +"amz_send_user.json"
    with open(file, 'a+') as f:
        wData = {"loginTime":loginTime,"loginIndex":loginIndex}
        print("asdada",wData)
        f.write(json.dumps(wData))

def getDatas(driver):
    headers = common.getHeader()
    url = "https://ebus-b1.test.api.sui10.com/json/amz_seller/query"
    global begins
    begins = readIndex()
    readIndexUser()
    data = {"req": {"begin": begins}}
    r = requests.post(url,
                      data=json.dumps(data),
                      headers=headers,
                      # proxies=proxies,
                      verify=False)
    if r.status_code == 200:
        print(begins)

        jsonData = json.loads(r.text)
        if jsonData["tars_ret"] == 0:
            data = jsonData["rsp"]["records"]
            if len(data) > 0:
                sData = json.loads(data[0]["data"])
                # print(sData)
                seleniumPage(driver,sData)
            getDatas(driver)
        else:
            print("没有了")
def getDataList():

    s = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=s)
    getDatas(driver)



nowUser=""
def loginEvent(driver):
    global loginTime, loginIndex,nowUser
    try:
        if len(amz_seller_massag_config.userConfig) > 0:
            nowUser = amz_seller_massag_config.userConfig[loginIndex]["user"]
            driver.find_element(by=By.ID, value="ap_email").send_keys(
                amz_seller_massag_config.userConfig[loginIndex]["user"])
            time.sleep(1)
            driver.find_element(by=By.ID, value="ap_password").send_keys(
                amz_seller_massag_config.userConfig[loginIndex]["password"])
            time.sleep(1)
            driver.find_element(by=By.ID, value="a-autoid-0").click()

        else:
            if myIndex % 2 == 0:
                driver.find_element(by=By.ID, value="ap_email").send_keys("bzwjyydqfp@rambler.ru")
            else:
                driver.find_element(by=By.ID, value="ap_email").send_keys("tjsqytwffz@rambler.ru")
            time.sleep(1)
            driver.find_element(by=By.ID, value="ap_password").send_keys("aaaaaa")
            time.sleep(1)
            driver.find_element(by=By.ID, value="a-autoid-0").click()
            time.sleep(5)
    except Exception as e:
        print("不需要登录")
def autoDeal(driver,item):
    global myIndex,loginTime,isStart,loginIndex,excelList,nowHelloIndex
    # readIndexUser()
    driver.get(item["AOKETE"])
    if isStart == False:
        time.sleep(5)
        loginEvent(driver)
        isStart = True
    # driver.get("https://www.bilibili.com/read/cv21384724")

    try:
        codeKey = driver.find_element(by=By.ID, value="auth-captcha-image")
        if codeKey:
            print("要输入验证码了")
            common.writeLog("error", "seleniumPage",
                            "{begin:" + str(begins) +",    user:"+ nowUser +",     index:"+
                            str(readIndex)+ ",   url:" + item["AOKETE"] + ",   shop:"
                            +item["soldName"]+",    ASIN:"+item["ASIN"]+",    seller:"+item["seller"]+"}",
                            "anz_seller_messaging")
            time.sleep(999)
            time.sleep(999)
            time.sleep(999)
            # 重新跑
            autoDeal(driver,item)
    except Exception as e:
        print("没有验证码")
        time.sleep(5)
        try:
            ll = driver.find_element(by=By.XPATH, value='//*[@class="smartcs-buttons-button"]')
            ll.click()
            time.sleep(2)
        except Exception as e:
            print("没有这个选项0") ##没有这个选项
        try:
            smartcsButtom = driver.find_element(by=By.XPATH, value='//*[@class="smartcs-buttons-button"]')
            smartcsButtom.click()
            time.sleep(3)
        except Exception as e:
            print("没有这个选项") ##没有这个选项
        try:
            smartcsButtom2 = driver.find_element(by=By.XPATH, value='//*[@class="smartcs-buttons-button"][6]')
            smartcsButtom2.click()
            time.sleep(5)
        except Exception as e:
            print("没有这个选项2") ##没有这个选项
        timeinput = driver.find_element(by=By.CLASS_NAME, value="textarea-input")
        if (nowHelloIndex == len(helloArr)-1):
           nowHelloIndex = 0
        else:
            if (begins%3 == 0):
                nowHelloIndex = nowHelloIndex + 1
        timeinput.send_keys(helloArr[nowHelloIndex])
        # timeinput.send_keys(amz_seller_massag_config.userConfig[loginIndex]["content"])
        time.sleep(2)
        if amz_seller_massag_config.userConfig[loginIndex]["image"]:
            driver.find_element(by=By.CLASS_NAME, value='attachment-input').send_keys(amz_seller_massag_config.userConfig[loginIndex]["image"])
        time.sleep(25)
        driver.find_element(by=By.XPATH, value='//*[@class="right-group"]/span').click()
        cleanIndex()
        time.sleep(1)
        writeIndex(begins)
        excelList["A"].append(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
        excelList["B"].append(nowUser)
        excelList["C"].append(str(begins))
        excelList["D"].append(item["AOKETE"])
        excelList["E"].append(item["soldName"])
        excelList["F"].append(item["ASIN"])
        excelList["G"].append(item["seller"])
        common.writeLog("success", "seleniumPage:", "{begin:" + str(begins) +",    user:"+ nowUser +",     index:"+
                        str(begins)+ ",   url:" + item["AOKETE"] + ",   shop:"
                        +item["soldName"]+",    ASIN:"+item["ASIN"]+",    seller:"+item["seller"]+"}",
                        "anz_seller_messaging")
        common.excelBuild(excelList,"send"+times)
        time.sleep(6)
        loginTime = loginTime + 1
        cleanIndexUser()
        time.sleep(1)
        writeIndexUser()



        if loginTime >= 10:
            cleanIndexUser()
            time.sleep(1)
            loginTime = 0
            writeIndexUser()

            if loginIndex < len(amz_seller_massag_config.userConfig) - 1:
                loginIndex = loginIndex + 1
                cleanIndexUser()
                time.sleep(1)
                writeIndexUser()
            else:
                print("没有配置用户了，结束")
                FinishEvent()
                sys.exit(0)

            driver.quit()
            time.sleep(1)
            isStart = False
            getDataList()
        time.sleep(5)

def seleniumPage(driver,item):
    if "AOKETE" in item and item["AOKETE"] != "":
        try:
            autoDeal(driver,item)
        except Exception as e:
            print(e)
    else:
        print("没有链接")
        cleanIndex()
        time.sleep(1)
        writeIndex(begins)

def FinishEvent():
    global loginTime,loginIndex
    loginTime = 0
    loginIndex = 0
    cleanIndexUser()
    time.sleep(1)
    writeIndexUser()
if __name__ == '__main__':   #入口函数
    # if len(amz_seller_massag_config.keysArr) <= 0:
    getTimes()
    getDataList()
    print("finish")
    FinishEvent()

    # else:
    #     artificialDeal()