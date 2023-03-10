import requests
import datetime
from lxml import etree
import math

# 配自己的代理
proxies ={

}

def parse_youtube(url):
    print("parsing youtube url:" + url)
    headers = {'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Connection': 'Keep-Alive',
               'Host': 'www.youtube.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}
    r = requests.get(url,
                     data=None,
                     headers=headers,
                     #proxies =proxies,
                     verify=False)

    if r.status_code == 200:
        html = etree.HTML(r.text)
        url = html.xpath('//script[@type="application/ld+json"]/text()')
        kv = eval(url[0])
        owner_channel = kv["itemListElement"][0]['item']['@id'].replace("\\","")
        owner_name = kv["itemListElement"][0]['item']['name']
        owner_about = owner_channel +"/about"

        r = requests.get(owner_about,
                         data=None,
                         headers=headers,
                         #proxies=proxies,
                         verify=False)

        if r.status_code == 200:
            html = etree.HTML(r.text)
            pass
        else:
            pass

    return None


def dispatch(*data):
    switcher = {
        "www.youtube.com": parse_youtube,
    }
    func = switcher.get(data[0])
    if func:
        return func(data[1].strip())
    else:
        print("No parser for " + data[0])


def search(keys):
    headers = {'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Connection': 'Keep-Alive',
               'Host':'www.google.com.hk', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

    url = 'https://www.google.com/search?q='
    for key in keys:
        url += key + "+"
    url = url[:len(url)-1]
    url += '&tbm=vid'
    r = requests.get(url,
                     data=None,
                     headers=headers,
                     #proxies=proxies,
                     verify=False)
    if r.status_code == 200:
        return r.text
    else:
        return None


if __name__ == '__main__':
    print("begin:" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

    rsp = search(["fc", "car"])
    if rsp:
        html = etree.HTML(rsp)
        url = html.xpath('//video-voyager//a[@data-ved]/@href')
        cite = html.xpath('//video-voyager//cite/text()')
        for item in set(zip(cite, url)):
            dispatch(*item)

    print("end:"+ datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
