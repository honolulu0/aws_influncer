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
import math
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
reStart = False
bspg = 0
ipIndex = 0 #第几个ip
times = ""
nowHelloIndex = 0
asin = ""
mail = ""
content = ""
seller=""
shopName=""
pageSize = 400
nowUser=""
helloArr=[
    "Hi，Amazon Seller.",
    "Hello, Amazon Seller.",
    "Howdy , Amazon Seller.",
    "How are you? Amazon Seller.",
    "What's up? Amazon Seller .",
    "Nice to meet to，Amazon Seller."
]
ip = [
     "http://103.45.150.149:16817",

]

# def getHeader():
#     headers = {}
#     headers[
#         "cookie"] = "_ga=GA1.2.839356809.1670468456; Hm_lvt_5763e499eacd42ac563739be7c43ffc7=1670594100,1670633929,1670805245,1670978517; _gid=GA1.2.1486065427.1671153836; md_pss_id=09c0330010180510f303c06f02905700106b0c608a0670bd; Hm_lpvt_5763e499eacd42ac563739be7c43ffc7=1671155836; _gat=1"
#     headers["authority"] = "amz.uimoe.com"
#     headers["accept"] = "application/json, text/javascript, */*; q=0.01"
#     headers["accept-encoding"] = "gzip, deflate, br"
#     headers["accept-language"] = "zh-CN,zh;q=0.9"
#     headers["authorization"] = "D9F486D1232B05BEF6C1F1E703DE9EDF058778E36C5383093"
#     headers["cache-control"] = "no-cache"
#     headers["content-length"] = "251"
#     headers["content-type"] = "application/json"
#     headers["pragma"] = "no-cache"
#     headers["x-requested-with"] = "XMLHttpRequest"
#     headers[
#         "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
#     return headers

def ImportAsinInfo(sendContent,status,errText):
    url = "http://175.178.91.130/api/Chat/Import"
    nowDate = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        "items": [
            {
                "user": nowUser,
                "mail": mail,
                "seller": seller,
                "sendTime": nowDate,
                "sendContent": sendContent,
                "status": status,
                "errText": errText,
                "shopName": shopName,
                "asin": asin
            }
        ]
    }
    print(data)
    r = requests.post(url,
                      data=json.dumps(data),
                      headers=common.getHeader2(),
                      # proxies=proxies,
                      verify=False,
                      timeout=30)
    if r.status_code == 200:
        print(r.content)
    else:
        print("纪录失败")

def getAnis(page):
    url="http://175.178.91.130/api/Home/ASINContent"
    np = 1
    if(page > 0):
        np = page
    data = {
        "page": np,
        "pageSize": pageSize,
        "export":False
    }
    r = requests.post(url,
                     data=json.dumps(data),
                     headers=common.getHeader2(),
                     # proxies=proxies,
                     verify=False,
                     timeout=30)
    print(r.status_code)
    print(r.content)
    jsonData = json.loads(r.content)

    if(r.status_code == 200):
        datas = jsonData["data"]["Items"]
        return datas
    else:
        ImportAsinInfo("","0","获取anis列表接口返回:"+str(r.status_code))
        print(r.status_code)
        return None

def ipChange():
    chromeOptions = webdriver.ChromeOptions()
    # http: // pr.roxlabs.cn: 4600
    # 设置代理
    chromeOptions.add_argument("--proxy-server="+ip[ipIndex])
    # 一定要注意，=两边不能有空格，不能是这样--proxy-server = http://202.20.16.82:10152
    driver = webdriver.Chrome(chrome_options=chromeOptions)
    getDatas(driver)
    # 查看本机ip，查看代理是否起作用
    # url = "https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&"
    #
    # browser.get(url)
    # print(browser.page_source)
def handle_request_err(status_code):
    if status_code == 503:
        print('被反爬虫拦截，休眠30分钟')
        ImportAsinInfo("", "0", "被拦截休眠后重启")
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
    global reStart,bspg,ipIndex
    file = r'./' +"amz_anis_send.json"
    with open(file, 'a+') as f:
        bspg = math.ceil((index+1) / 18)  #相当于第几页
        if ((index+1) == 18 * bspg):
            if len(ip) > ipIndex:
                ipIndex = ipIndex+1
            else:
                ipIndex = 0
            reStart = True
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
        f.write(json.dumps(wData))

def getDatas(driver):
    global begins,asin,isStart,reStart,bspg
    begins = readIndex()
    pages = math.ceil((begins+1)/pageSize)
    data = getAnis(pages)
    readIndexUser()
    bspg = math.ceil(begins/18)    #相当于第几页
    if(begins == 18*bspg and reStart):
        isStart = False
        ipChange()
    else:
        print(begins)
        print(((pages)*pageSize))
        if len(data)>0 and ((pages)*pageSize)-1 >= begins and len(data)-1+((pages-1)*pageSize) >= begins:
            asin = data[begins-((pages-1)*pageSize)]["Content"]
            url = "https://www.amazon.com/dp/"+asin
            #开始处理
            autoDeal(driver,url)
            getDatas(driver)
        else:
            print("没有了")
            ImportAsinInfo("", "0", "anis列表爬取结束，需要上传新的文件")
            FinishEvent()

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
                ImportAsinInfo("", "0", "登录界面没有用户输入框")
            try:
                driver.find_element(by=By.ID, value="ap_password").send_keys(
                    amz_anis_data.userConfig[loginIndex]["password"])
                time.sleep(1)
                driver.find_element(by=By.ID, value="a-autoid-0").click()
            except Exception as e:
                print("没有密码输入")
                ImportAsinInfo("", "0", "登录界面没有密码输入框")
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
        ImportAsinInfo("", "0", "登录界面没有用户输入框")
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
        ImportAsinInfo("", "0", "登录界面没有密码输入框")
    try:
        codeKey = driver.find_element(by=By.ID, value="auth-captcha-image")
        if codeKey:
            print("要输入验证码了")
            ImportAsinInfo("", "0", "需要输入验证码,需要手动重启")
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
    global myIndex,loginTime,isStart,loginIndex,nowHelloIndex,content,seller,shopName
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
                ImportAsinInfo("", "0", "需要输入验证码，需要手动重启")
                #需要纪录失败
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
            time.sleep(2)
            if amz_anis_data.userConfig[loginIndex]["image"]:
                driver.find_element(by=By.CLASS_NAME, value='attachment-input').send_keys(amz_anis_data.userConfig[loginIndex]["image"])
            time.sleep(20)
            driver.find_element(by=By.XPATH, value='//*[@class="right-group"]/span').click()
            cleanIndex()
            time.sleep(1)
            writeIndex(begins)
            # 需要纪录成功
            # common.writeLog("success", "成功发信:", "{begin:" + str(begins) +"url:"+url+"}",
            #                 "amzanis_send")
            print("发信成功")
            ImportAsinInfo(helloArr[nowHelloIndex], "1", "成功发信")
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
                    reSetUserEvent()

                driver.quit()
                time.sleep(1)
                isStart = False
                ipChange()
            time.sleep(5)
    except Exception as e:
        common.writeLog("error", "No send",
                        "{url:" +url+"}",
                        "anz_anis_send")
        ImportAsinInfo("", "3", "没有店铺，可能是亚马逊直营")
        cleanIndex()
        time.sleep(1)
        writeIndex(begins)
        time.sleep(1)

def reSetUserEvent():
    # 用户从第一个开始
    global loginTime,loginIndex
    loginTime = 0
    loginIndex = 0
    cleanIndexUser()
    time.sleep(1)
    writeIndexUser()
    print("用户重置从第一个开始")
def FinishEvent():
    print("结束了，等待重启")
    time.sleep(999)
    time.sleep(999)
    time.sleep(999)
    ipChange()
if __name__ == '__main__':   #入口函数
    ipChange()
    # ImportAsinInfo("www","0","111")
    # getAnis(1)