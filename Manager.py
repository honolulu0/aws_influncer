import socket
import threading
import sys
import os
import time
import platform
import random
import json
import requests
import datetime
import common
from functools import reduce

# Variables for holding information about connections
connections = []

cls = []
classArr = []
nowClassIndex = 0
def queryClass():
    url = "https://ebus-b1.test.api.sui10.com/json/external/queryClass"
    headers = common.getHeader()
    r = requests.get(url,
                     data='{"req": {"token": ""}}',
                     headers=headers,
                     # proxies=proxies,
                     verify=False)
    if r.status_code == 200:
        jsonData = json.loads(r.text)
        if jsonData["tars_ret"] == 0:
            global classArr
            global cls
            classArr = jsonData["rsp"]["classes"]
            for a in jsonData["rsp"]["classes"]:
                cls.append({
                        "name": a["name"],
                        "cid": a["id"],
                        "last_update": 0,
                        "tags": []
                    })
    else:
        return

def getKeys(cid):   #获取关键字
    headers = common.getHeader()
    url = 'https://ebus-b1.test.api.sui10.com/json/external/key'
    data = {
        "req":{"token": "",
               "cid":cid
               }
    }
    r = requests.get(url,
                     data=json.dumps(data),
                     headers=headers,
                     # proxies=proxies,
                     verify=False)
    jsonData = json.loads(r.content)
    print(r.content)
    if r.status_code == 200:
        return jsonData['rsp']
    else:
        return None

class Client(threading.Thread):
    CLIENT_CLOSE = 0  # 主动退出
    CLIENT_HANG = 1  # 被动关闭

    def __init__(self, socket, address, id, name, signal):
        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.name = name
        self.signal = signal

    def __str__(self):
        return str(self.id) + " " + str(self.address)

    def destory(self, reason):
        global connections
        print("客户端 " + str(self.address) + " 已经断开:" + str(reason))
        self.signal = False
        connections.remove(self)

    def run(self):
        while self.signal:
            try:
                data = self.socket.recv(32)
                print(str(os.getpid()) + "接收到客户端数据: " + str(data.decode("utf-8")))
            except:
                self.destory(self.CLIENT_CLOSE)
                break
            if len(data) != 0:
                print("ID " + str(self.id) + ": " + str(data.decode("utf-8")))
            else:
                self.destory(self.CLIENT_HANG)

# Wait for new connections
def newConnections(socket):
    while True:
        now = datetime.datetime.now()
        sock, address = socket.accept()
        connections.append(Client(sock, address, len(connections), "Name", True))
        connections[len(connections) - 1].start()
        print("接受到新链接， ID " + str(connections[len(connections) - 1]))
        # 当客户端链接成功时，下发tag给它
        if len(classArr) > 0:
            latest = reduce(lambda pre, cur: cur if cur["last_update"] < pre["last_update"] else pre, cls)
            print("last",latest)
            keys = getKeys(latest["cid"])
            latest["last_update"] = int(time.time())
            latest["keys"] = keys["keys"]
            jsonKeys = {
                "id":latest["cid"],
                "keys":keys["keys"]
            }
            sock.sendall(str.encode(str(json.dumps(jsonKeys))))
        else:
            print("class没有加载进来")


def Warden():
    while True:
        if len(connections) < 5:#3
            print("当前总共有少于3个爬虫在工作， 启动一个新的")
            cmd = sys.executable + " Client.py"
            osName = platform.system()
            if (osName == 'Windows'):
                cmd = "start " + cmd
            elif (osName == 'Linux'):
                cmd = cmd + " &"
            elif (osName == 'Darwin'):
                cmd = cmd + " &"

            os.system(cmd)
            time.sleep(3)


def main():
    host = "localhost"
    port = 31999
    # Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)

    newConnectionsThread = threading.Thread(target=newConnections, args=(sock,))
    newConnectionsThread.start()

    warden = threading.Thread(target=Warden)
    warden.start()


if __name__ == '__main__':   #入口函数
    queryClass()
    main()
