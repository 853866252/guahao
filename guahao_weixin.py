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
import lxml
import datetime
robot = werobot.WeRoBot(token='ce1Jcs')

def get_source(url):
    session = requests.session()
    source = session.get(url).content
    return source.decode('utf-8')

def get_verify():
    url = 'http://book.xachyy.com/modules/verifyImage.ashx'
    session = requests.session()
    response_headers = session.get(url).headers
    session_id = ''.join(re.findall('ASP.NET_SessionId=(.*); path=/;',response_headers['Set-Cookie']))
    code_id = ''.join(re.findall('HBHOSPITALCODE=(\d\d\d\d)',response_headers['Set-Cookie']))
    return session_id,code_id

def get_patientId(weixin_session,session_id,code_id,indentify_id,password):
    client = pymongo.MongoClient(host='172.17.76.183',port=27017)
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
        patient['session'] = weixin_session.encode('utf-8')
        patient['Accoutid'] = a[0]
        print patient
        col.insert(patient)
        return "登录成功"
    else:
        return "登录用户名或密码错误，请重新输入"

def get_book_time(html):
#    print html
    date_time = {}
    dt_time = lxml.html.document_fromstring(html)
    doctor_date = dt_time.xpath('//img/@onclick')
#    print doctor_date[0]
    for each in doctor_date:
        time = each.split('\',\'')
#        print time
        date_time['Date'] = time[1]
        date_time['Time'] = time[3]
        break
    return date_time

def get_book_items(doctor_info):

    date1 = str(datetime.date.today().replace(day=1))
    date2 = str(datetime.date.today().replace(day=1) - datetime.timedelta(-31))
    datelist = [date1,date2]
    date_time = {}
#    print doctor_info['ClinicLabelId'].encode("utf-8")
    for each in datelist:
        #doctor_info['ClinicLabelId']encode("utf-8")
        url = 'http://book.xachyy.com/Doctor/ajax.aspx?param=GetBookInfoByDoctorId&uimode=1&clinicLabelId='+doctor_info['ClinicLabelId'].encode("utf-8")+'&cliniclabeltype=2&clinicweektype=0&rsvmodel=1&doctorid='+doctor_info['DoctorID'].encode("utf-8")+'&selectTime='+each
        html = get_source(url)
        date_time = get_book_time(html)
        if date_time != {}:
            break
    if date_time == {}:
        print "not start"
    else:
        return date_time


def register(doctor_info,date_time):
    cookie = {'Cookie':'_gscu_511672516=98488034m3kugq10; Hm_lvt_70ded3ee32333aff6a77cf99eec6f0f8=1498488193,1498488194,1498489857,1499003956; Hm_lpvt_70ded3ee32333aff6a77cf99eec6f0f8=1499009739; ASP.NET_SessionId=v2cxqnaqpbf1rocazpr1o5t4; HBHOSPITALCODE=2953; Passport_Service=865EAD1375C8E57D9DA23CDF2D7AC06DF5AEB7AD4524CE2C19C08BEEB2C7958B0E7438193E79C85F7AFB66037BB96D85C32BAA46EDBA3DEE2E31E2056E2EA625924A2028D71E4923464CCCF480C991E302DFC51D20E8F7485992EDCC3AA344490F8C15DE723CF0E24095E6955F6898659BF81C455FCC66399F113292185C5E2BBF51794384628D4C5B489E4D8F4FB1D8FB025420F8A0DE571558C32BAC5F24980FC064DD074EB8CEA861A65AEE69DAB6FC399224E873990E1B71125EC60D49DEEE122204CAF6997B1992361135C8E0A6B0E1C2261DE156D839151B06D3F000035052E9A2CCC3033788996786CE0F0318532D0EE6EE805B9006E13D8EE4295596AFB500C39092ABB8D9D4216D; login=610100211001776408'}
    url = 'http://book.xachyy.com/Doctor/ajax.aspx?param=order&hospitalId=61010021&patientId=610100211001776408&clinicLabelId='+doctor_info['ClinicLabelId'].encode("utf-8")+'&clinicDate='+date_time['Date']+'&timePartType=1&timePart='+date_time['Time']+'&channcelType=3&rsvmodel=1&returnVisitId=1'
    session = requests.Session()
    html = session.post(url).content
    print html

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
        client = pymongo.MongoClient(host='172.17.76.183',port=27017)
        database = client.xachyy_DBS
        col = database.doctor_info
        doctor_name = col.find({'Name': task[1].encode('utf-8')})
        for each in doctor_name:
            doctor_info = each
        date_time = get_book_items(doctor_info)
        back = register(doctor_info, date_time)
        return back

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