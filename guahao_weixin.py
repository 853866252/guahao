#/usr/bin/env python
# -*- coding: UTF-8 -*-
import werobot
import sqlite3
from werobot import WeRoBot
import requests

robot = werobot.WeRoBot(token='ce1Jcs')


@robot.subscribe
def intro(message):
    return "欢迎来到任式机器，目前提供自动预定挂号抢号服务。\n想挂号请输入1"

@robot.text
def hello(message, session):
    url = 'http://www.tuling123.com/openapi/api'
    datas = {}
    datas['key'] = '852a620fce214d28bb635e074ebb7fba'
    datas['info'] = message.content
    conn = sqlite3.connect('werobot_session.sqlite3')
    cursor = conn.execute("SELECT id FROM WeRoBot")
    for row in cursor:
        print row
    id = message.source
    print id
    html = requests.post(url,data=datas).content
    return eval(html)['text']

 #   if message == '1':
#        return
#    print session
#    print message
#    count = session.get("count", 0) + 1
#    print session
#    session["count"] = count
#    return "Hello! You have sent %s messages to me" % count



robot.config['HOST'] = '172.17.76.183'
robot.config['PORT'] = 80

#robot.config["APP_ID"] = "你的 AppID"
#robot.config["APP_SECRET"] = "你的 AppSecret"
#client = robot.client

robot.run()