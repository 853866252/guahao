#/usr/bin/env python
# -*- coding: UTF-8 -*-
import werobot
from werobot import WeRoBot
robot = werobot.WeRoBot(token='ce1Jcs')


@robot.subscribe_event
def intro(message):
    return "欢迎来到任式机器，目前提供自动预定挂号抢号服务"

@robot.text
def hello(message, session):
    count = session.get("count", 0) + 1
    session["count"] = count
    return "Hello! You have sent %s messages to me" % count






robot.config['HOST'] = '172.17.76.183'
robot.config['PORT'] = 80

#robot.config["APP_ID"] = "你的 AppID"
#robot.config["APP_SECRET"] = "你的 AppSecret"
#client = robot.client

robot.run()