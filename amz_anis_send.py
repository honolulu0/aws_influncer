import json
import sys
import threading
import time
import random
import requests
import datetime
import urllib3
import common
import amz_anis_data
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
anis = ""
mail = ""
content = ""
seller=""
shopName=""
helloArr=[
    "Hi，Amazon Seller.",
    "Hello, Amazon Seller.",
    "Howdy , Amazon Seller.",
    "How are you? Amazon Seller.",
    "What's up? Amazon Seller .",
    "Nice to meet to，Amazon Seller."
]

def test():
    chromeOptions = webdriver.ChromeOptions()

    # 设置代理
    chromeOptions.add_argument("--proxy-server=http://pr.roxlabs.cn:4600")
    # 一定要注意，=两边不能有空格，不能是这样--proxy-server = http://202.20.16.82:10152
    browser = webdriver.Chrome(chrome_options=chromeOptions)

    # 查看本机ip，查看代理是否起作用
    url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"

    browser.get(url)
    # print(browser.page_source)


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
    file = r'./' +"amz_anis_send.json"
    with open(file, 'r') as f:
        # f.write(newContext)
        data = f.read()
        wirteData = "1"
        if data:
            wirteData = data
        print(wirteData)
        return int(wirteData)
def cleanIndex():
    file = r'./' + "amz_anis_send.json"
    with open(file, 'w') as f:
        f.write("")
def writeIndex(index):
    file = r'./' +"amz_anis_send.json"
    with open(file, 'a+') as f:
        f.write(str(index+1))
def readIndexUser():
    global loginTime,loginIndex
    file = r'./' +"amz_anis_user.json"
    with open(file, 'r') as f:
        # f.write(newContext)
        data = f.read()
        if data:
            wirteData = json.loads(data)
            loginTime = wirteData["loginTime"]
            loginIndex =  wirteData["loginIndex"]

def cleanIndexUser():
    file = r'./' + "amz_anis_user.json"
    with open(file, 'w') as f:
        f.write("")
def writeIndexUser():
    file = r'./' +"amz_anis_user.json"
    with open(file, 'a+') as f:
        wData = {"loginTime":loginTime,"loginIndex":loginIndex}
        print("asdada",wData)
        f.write(json.dumps(wData))

def getDatas(driver):
    global begins,anis
    begins = readIndex()
    data = amz_anis_data.config
    readIndexUser()
    if len(data)-1 >= begins:
        anis = data[begins]
        url = "https://www.amazon.com/dp/"+anis
        seleniumPage(driver, url)
        getDatas(driver)
    else:
        print("没有了")
        cleanIndex()
        time.sleep(1)
        begins = 0
        writeIndex(begins)
def getDataList():
    s = Service("chromedriver.exe")
    driver = webdriver.Chrome(service=s)
    getDatas(driver)

nowUser=""
def loginEvent(driver):
    global loginTime, loginIndex,nowUser,mail
    try:
        if len(amz_anis_data.userConfig) > 0:
            nowUser = amz_anis_data.userConfig[loginIndex]["user"]
            try:
                driver.find_element(by=By.ID, value="ap_email").send_keys(
                    amz_anis_data.userConfig[loginIndex]["user"])
                mail = amz_anis_data.userConfig[loginIndex]["user"]
                time.sleep(1)
            except Exception as e:
                print("没有用户输入")
            try:
                driver.find_element(by=By.ID, value="ap_password").send_keys(
                    amz_anis_data.userConfig[loginIndex]["password"])
                time.sleep(1)
                driver.find_element(by=By.ID, value="a-autoid-0").click()
            except Exception as e:
                print("没有密码输入")

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
def IloginIn(driver):

    global loginTime, loginIndex, nowUser,mail
    url =  "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
    driver.get(url)
    time.sleep(1)
    try:
        nowUser = amz_anis_data.userConfig[loginIndex]["user"]
        driver.find_element(by=By.XPATH, value='//*[@class="a-input-text a-span12 auth-autofocus auth-required-field"]').send_keys(amz_anis_data.userConfig[loginIndex]["user"])
        mail = amz_anis_data.userConfig[loginIndex]["user"]
        time.sleep(1)
        driver.find_element(by=By.XPATH,
                            value='//*[@class="a-button-inner"]').click()
        time.sleep(1)
    except Exception as e:
        print("没有用户输入")
    try:
        driver.find_element(by=By.XPATH,
                            value='//*[@id="ap_password"]').send_keys(
            amz_anis_data.userConfig[loginIndex]["password"])
        time.sleep(1)
        driver.find_element(by=By.XPATH,
                            value='//*[@id="signInSubmit"]').click()
    except Exception as e:
        print("没有密码输入")

    try:
        codeKey = driver.find_element(by=By.ID, value="auth-captcha-image")
        if codeKey:
            print("要输入验证码了")
            common.writeLog("error", "需要输入验证码",
                            "{begin:" + str(begins)+"url:"+url + "}",
                            "anz_anis_send")
            time.sleep(999)
            time.sleep(999)
            time.sleep(999)
            driver.find_element(by=By.XPATH,
                                value='//*[@id="signInSubmit"]').click()
            time.sleep(2)
            # 重新跑
            autoDeal(driver, url)
    except Exception as e:
        print("IloginIn没有验证码,直接登录")
    try:
        notNow = driver.find_element(by=By.ID, value="ap-account-fixup-phone-skip-link")
        notNow.click()
    except Exception as e:
        print("没有notnow")

def autoDeal(driver,url):
    global myIndex,loginTime,isStart,loginIndex,excelList,nowHelloIndex,content,seller,shopName
    if isStart == False: #第一次进来主动登录
        IloginIn(driver)
        isStart = True
    time.sleep(2)
    driver.get(url)
    # "nav-signin-tooltip"
    time.sleep(2)
    try:
        sellerProfileTriggerId = driver.find_element(by=By.ID, value="sellerProfileTriggerId")
        shopName = sellerProfileTriggerId.get_attribute("innerHTML")
        sellerProfileTriggerId.click()
        time.sleep(2)
        sellerCcontactButton = driver.find_element(by=By.XPATH, value='//*[@id="seller-contact-button"]/span/a')
        href = sellerCcontactButton.get_dom_attribute("href")
        result = parse.urlparse(href)
        query_dict = parse.parse_qs(result.query)
        seller = ""
        # print(query_dict)
        if len(query_dict["sellerID"]) > 0:
            seller = query_dict["sellerID"][0]
        print("seller",seller,shopName)
        driver.get(href)
        time.sleep(2)
        if isStart == False:
            time.sleep(5)
            loginEvent(driver)
            isStart = True
        try:
            codeKey = driver.find_element(by=By.ID, value="auth-captcha-image")
            if codeKey:
                print("要输入验证码了")
                common.writeLog("error", "需要输入验证码",
                                "{begin:" + str(begins) + "url:" + url + "}",
                                "anz_anis_send")
                time.sleep(999)
                time.sleep(999)
                time.sleep(999)
                # 重新跑
                autoDeal(driver,url)
        except Exception as e:
            print("没有验证码")
            time.sleep(3)
            ll = driver.find_element(by=By.XPATH, value='//*[@class="smartcs-buttons-button"]')
            ll.click()
            time.sleep(2)
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
            content = helloArr[nowHelloIndex]
            # timeinput.send_keys(amz_anis_data.userConfig[loginIndex]["content"])
            time.sleep(2)
            if amz_anis_data.userConfig[loginIndex]["image"]:
                driver.find_element(by=By.CLASS_NAME, value='attachment-input').send_keys(amz_anis_data.userConfig[loginIndex]["image"])
            time.sleep(20)
            driver.find_element(by=By.XPATH, value='//*[@class="right-group"]/span').click()
            cleanIndex()
            time.sleep(1)
            writeIndex(begins)
            common.writeLog("success", "成功发信:", "{begin:" + str(begins) +"url:"+url+"}",
                            "amzanis_send")
            time.sleep(6)
            loginTime = loginTime + 1
            cleanIndexUser()
            time.sleep(1)
            writeIndexUser()

            if loginTime >= 2:
                cleanIndexUser()
                time.sleep(1)
                loginTime = 0
                writeIndexUser()

                if loginIndex < len(amz_anis_data.userConfig) - 1:
                    loginIndex = loginIndex + 1
                    cleanIndexUser()
                    time.sleep(1)
                    writeIndexUser()
                else:
                    print("没有配置用户了，结束")
                    FinishEvent()

                driver.quit()
                time.sleep(1)
                isStart = False
                getDataList()
            time.sleep(5)
    except Exception as e:
        common.writeLog("error", "No send",
                        "{url:" +url+"}",
                        "anz_anis_send")
        cleanIndex()
        time.sleep(1)
        writeIndex(begins)
        time.sleep(1)

        print("没有店铺，可能是亚马逊直营")



def seleniumPage(driver,url):
        try:
            autoDeal(driver,url)
        except Exception as e:
            print(e)

def FinishEvent():
    global loginTime,loginIndex
    loginTime = 0
    loginIndex = 0
    cleanIndexUser()
    time.sleep(1)
    writeIndexUser()
    print("从第一个开始")
    getDataList()
if __name__ == '__main__':   #入口函数
    getTimes()
    getDataList()
    print("finish")
    FinishEvent()
