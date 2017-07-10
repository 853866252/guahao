#/usr/bin/env python
# -*- coding: UTF-8 -*-
import werobot
import sqlite3
from werobot import WeRoBot
import hashlib
import requests
import re
import urllib2
import pymongo
robot = werobot.WeRoBot(token='ce1Jcs')

def get_verify():
    url = 'http://book.xachyy.com/modules/verifyImage.ashx'
    session = requests.session()
    response_headers = session.get(url).headers
    session_id = ''.join(re.findall('ASP.NET_SessionId=(.*); path=/;',response_headers['Set-Cookie']))
    code_id = ''.join(re.findall('HBHOSPITALCODE=(\d\d\d\d)',response_headers['Set-Cookie']))
    return session_id,code_id

def get_patientId(weixin_session,session_id,code_id,indentify_id,password):
    client = pymongo.MongoClient()
    database = client.Patient
    col = database.Patient_info
    patient = {}
    i = 'ASP.NET_SessionId={session}; HBHOSPITALCODE={code}'.format(session=session_id,code=code_id)
    cookie = {'Cookie': i}
    print cookie
    url = 'http://book.xachyy.com/passport/SsoLogin.aspx?user={user}&pwd={pwd}&app=0&loginType=2-1&hospitalId=61010021&verifycode={code}'.format(user=indentify_id,pwd=password,code=code_id)
    print url
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie',i))
    f = opener.open(url)
    a = re.findall('"Accountid":"(.*)","Accountname', f.read())
    if a:
        print weixin_session
        print type(weixin_session)
#        patient['session'] = weixin_session
        patient['Accoutid'] = a[0]
        col.insert(patient)
        return "登录成功"
    else:
        return "登录用户名或密码错误，请重新输入"

@robot.subscribe
def intro(message):
    return "欢迎来到任式机器，目前提供自动预定挂号及抢号服务。\n挂号分为两个步骤：\n1）输入：登录/用户名/密码（仅需一次）\n2）输入：挂号/医生名称/现在或抢号"

@robot.text
def hello(message, session):
    task = message.content
    task = task.split('/')
    print task
    type(task[0])
    if task[0].encode('utf-8') == '登录':
        session_id, code_id = get_verify()
        identify_id = task[1].encode('utf-8')
        password = hashlib.md5(task[2].encode('utf-8')).hexdigest()
        back = get_patientId(message.source,session_id, code_id, identify_id, password)
        return back

    elif task[0].encode('utf-8') == '挂号':
        return "2"

    else:
        url = 'http://www.tuling123.com/openapi/api'
        datas = {}
        datas['key'] = '852a620fce214d28bb635e074ebb7fba'
        datas['info'] = message.content
        id = message.source
        datas['userid'] = id
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