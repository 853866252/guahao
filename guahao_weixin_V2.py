#/usr/bin/env python
# -*- coding: UTF-8 -*-
import werobot
import sqlite3
import pytesseract
from PIL import Image
import hashlib
import requests
import re
import urllib2
import pymongo
import lxml
import lxml.html
import datetime
import ssl
from werobot.replies import TextReply

ssl._create_default_https_context = ssl._create_unverified_context


robot = werobot.WeRoBot(token='ce1Jcs')
robot.config["APP_ID"] = "wxbc74d8ad0c8b6a18"
robot.config["APP_SECRET"] = "2ed273df5736c71f306d6cf22ed835ae"

#menu_data={
#    "button":[{
#         "type": "click",
#         "name": "今日歌曲",
#         "key": "music"
#    }]
#}
#
#robot.client.create_menu(menu_data)





client_db = pymongo.MongoClient(host='172.17.76.183', port=27017)
database1 = client_db.Register
database2 = client_db.Hospital_DBS
col1 = database1.Transaction
col2 = database2.doctor_xachyy_info
col3 = database1.Patient_info
col4 = database1.Transaction_plan
col5 = database2.doctor_xijing_info

def get_source(url):
    session = requests.session()
    source = session.get(url).content
    return source.decode('utf-8')

def get_verify_xachyy(hospital_url):
    url = 'http://{URL}/modules/verifyImage.ashx'.format(URL=hospital_url)
    session = requests.session()
    response_headers = session.get(url).headers
    session_id = ''.join(re.findall('ASP.NET_SessionId=(.*); path=/;',response_headers['Set-Cookie']))
    code_id = ''.join(re.findall('HBHOSPITALCODE=(\d\d\d\d)',response_headers['Set-Cookie']))
    return session_id,code_id
def get_verify_xijing(hospital_url):
    url = 'http://{URL}/modules/verifyImage.ashx'.format(URL=hospital_url)
    session = requests.session()
    response = session.get(url)
    response_headers = response.headers
    response_data = response.content
    file = open('image.jpg', 'wb')
    file.write(response_data)
    file.close()
    image = Image.open('image.jpg')
    code = pytesseract.image_to_string(image)
    session_id = ''.join(re.findall('ASP.NET_SessionId=(.*); path=/;', response_headers['Set-Cookie']))
    #    code_id = ''.join(re.findall('HBHOSPITALCODE=(\d\d\d\d)',response_headers['Set-Cookie']))
    print session_id,code
    return session_id, code

def get_patientId_xachyy(weixin_session,session_id,code_id,indentify_id,password,hospital_url):


    patient = {}
    i = 'ASP.NET_SessionId={session}; HBHOSPITALCODE={code}'.format(session=session_id,code=code_id)
    login_url = 'http://{URL}/passport/SsoLogin.aspx?user={user}&pwd={pwd}&app=0&loginType=2-1&hospitalId=&verifycode={code}'.format(URL=hospital_url,user=indentify_id,pwd=password,code=code_id)
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie',i))
    f = opener.open(login_url)
    a = re.findall('"Accountid":"(.*)","Accountname', f.read())

    if a:
        patient['Session'] = weixin_session.encode('utf-8')
        patient['Accoutid'] = a[0]
        patient['Url'] = hospital_url
        col3.insert(patient)
        return "登录成功"
    else:
        return "登录用户名或密码错误，请重新输入"

def get_patientId_xijing(weixin_session, indentify_id, password, hospital_url):

    patient = {}
    while hospital_url:
        session_id,code_id = get_verify_xijing(hospital_url)
        i = 'ASP.NET_SessionId={session}; HBHOSPITALCODE={code}'.format(session=session_id, code=code_id)
        login_url = 'http://{URL}/passport/SsoLogin.aspx?user={user}&pwd={pwd}&app=0&loginType=1-1&hospitalId=&verifycode={code}'.format(
            URL=hospital_url, user=indentify_id, pwd=password, code=code_id)
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', i))
        f = opener.open(login_url)
        b = re.findall("login_state='(.*)'\;", f.read())
        print b
        print type(b)
        if b[0] == '验证码错误':
            continue
        elif b[0]=='error':
            return "登录用户名或密码错误，请重新输入"

        else:
            a = re.findall('"Accountid":"(.*)","Accountname', b[0])
            print a
            if a:
                patient['Session'] = weixin_session.encode('utf-8')
                patient['Accoutid'] = a[0]
                patient['Url'] = hospital_url
                col3.insert(patient)
                return "登录成功"
            else:
                return "登录用户名或密码错误，请重新输入"

def get_book_time(html):
    date_time = {}
    dt_time = lxml.html.document_fromstring(html)
    doctor_date = dt_time.xpath('//img/@onclick')
    for each in doctor_date:
        time = each.split('\',\'')
        date_time['Date'] = time[1]
        date_time['TimePartType'] = time[2]
        date_time['Time'] = time[3]
        break
    return date_time

def get_book_items(doctor_info,URL):
    print URL
    print type(URL)
    date1 = str(datetime.date.today().replace(day=1))
    date2 = str(datetime.date.today().replace(day=1) - datetime.timedelta(-31))
    datelist = [date1,date2]
    date_time = {}
    print datelist
    for each in datelist:
        url = 'http://{URL2}/Doctor/ajax.aspx?param=GetBookInfoByDoctorId&uimode=1&clinicLabelId={ClinicLabel}&cliniclabeltype=2&clinicweektype=0&rsvmodel=1&doctorid={DoctorID}&selectTime={time}'.format(URL2=URL,ClinicLabel=doctor_info['ClinicLabelId'].encode("utf-8"),DoctorID=doctor_info['DoctorID'].encode("utf-8"),time=each)
        print url
        html = get_source(url)
        date_time = get_book_time(html)
        if date_time != {}:
            break
    return date_time


def register(patient_info,doctor_info,date_time,URL):
    if URL == 'book.xachyy.com':
        url = 'http://{URL1}/Doctor/ajax.aspx?param=order&hospitalId=61010021&patientId={patientid}&clinicLabelId='.format(URL1=URL,patientid=patient_info['Accoutid'])+doctor_info['ClinicLabelId'].encode("utf-8")+'&clinicDate='+date_time['Date']+'&timePartType='+date_time['TimePartType']+'&timePart='+date_time['Time']+'&channcelType=3&rsvmodel=1&returnVisitId=1'
    elif URL == 'www.83215321.com':
        url = 'http://{URL1}/Doctor/ajax.aspx?param=order&hospitalId=61010001&patientId={patientid}&clinicLabelId='.format(URL1=URL,patientid=patient_info['Accoutid'])+doctor_info['ClinicLabelId'].encode("utf-8")+'&clinicDate='+date_time['Date']+'&timePartType='+date_time['TimePartType']+'&timePart='+date_time['Time']+'&channcelType=3&rsvmodel=1&returnVisitId=1'
    session = requests.Session()
    html = session.post(url).content
    print html
    print type(html)
    return html

def get_verify_register(session,url):
    if col3.find_one({'Session': session,'Url':url}) == None:
        return "请按照如下格式进行登录验证，（登录/用户名/密码），此登录仅需一次,若没有账号请先到官网注册"
    else:
        task = col1.find_one({'Session': session})
        if task['Time'].encode('utf-8') == '现在' and task['Hospital'].encode('utf-8') == '西安市儿童医院':
            doctor_info = col2.find_one({'Name': task['Doctor']})
            patientinfo = col3.find_one({'Session': session,'Url':url})
            print patientinfo
            date_time = get_book_items(doctor_info,patientinfo['Url'].encode("utf-8"))
            if date_time != {}:
                back1 = register(patientinfo, doctor_info, date_time,url)
                col1.delete_one({'Session': session})
                print 4
                print back1
                print type(back1)
                return (back1)
            else:
                return "挂号没有开始或者已经预定完！\n请输入3取消预约该预约流程。\n\n您也可以选择其他医生或者选择明日抢号"
        elif task['Time'].encode('utf-8') == '现在' and task['Hospital'].encode('utf-8') == '西京医院':
            doctor_info = col5.find_one({'Name': task['Doctor']})
            patientinfo = col3.find_one({'Session': session,'Url':url})
            date_time = get_book_items(doctor_info,patientinfo['Url'])
            if date_time != {}:
                back2 = register(patientinfo, doctor_info, date_time,url)
                col1.delete_one({'Session': session})
                return back2
            else:
                return "挂号没有开始或者已经预定完！\n请输入3取消预约该预约流程。\n\n您也可以选择其他医生或者选择明日抢号"
        else:

            col4.insert(task)
            col1.delete_one({'Session': session})
            return "已经准备明天为您抢号，请耐心等待"

#@check
def sign_in(hospital_url,task,message):
    if hospital_url == 'book.xachyy.com':
        session_id, code_id = get_verify_xachyy(hospital_url)
        identify_id = task[1].encode('utf-8')
        password = hashlib.md5(task[2].encode('utf-8')).hexdigest()
        back = get_patientId_xachyy(message.source, session_id, code_id, identify_id, password, hospital_url)
        return back + "\n请输入确定，完成任务下达"
    elif hospital_url == 'www.83215321.com':
        identify_id = task[1].encode('utf-8')
        password = hashlib.md5(task[2].encode('utf-8')).hexdigest()
        back = get_patientId_xijing(message.source, identify_id, password, hospital_url)
        return back + "\n请输入确定，完成任务下达"
    else:
        return "请重新输入序号：\n1.西京\n2.西安市儿童医院\n3.取消挂号"

#def check(fuc):
#    if col3.find_one({'Session': message.source, 'Url': hospital_url}) == None:
#        sign_back = sign_in(hospital_url, task, message)
#        return sign_back
#    else:
#        return "已经成功登录，请继续挂号"
metadate = {
    "button":[{
         "type": "click",
         "name": "今日歌曲",
         "key": "music"
    }]
}

werobot.client.Client.create_menu(metadate)

@robot.subscribe
def intro(message):
    return "欢迎来到任式机器，公众号提供自动预定挂号及抢号服务。预想挂号请输入：挂号（目前仅支持西安市儿童医院）"

@robot.key_click("music")
def music(message):
    return '你点击了“今日歌曲”按钮'

@robot.text
def hello(message, session):
    trans = col1.find_one({'Session':message.source.encode('utf-8')})
    if trans != None:
        news = message.content
        task = news.split('/')
        if task[0].encode('utf-8') == '登录':
            hospital_url = trans['Url']
            if col3.find_one({'Session': message.source, 'Url': hospital_url}) == None:
                sign_back = sign_in(hospital_url, task, message)
                return sign_back
            else:
                return "已经成功登录，请继续挂号"

        if news.encode('utf-8') == '3':
            col1.delete_one({'Session': message.source.encode('utf-8')})
            col4.delete_one({'Session': message.source.encode('utf-8')})
            return "已经取消挂号流程"
        if trans['Hospital'] == '':
            if news.encode('utf-8') == '1':
                col1.update({'Session': message.source.encode('utf-8')}, {'$set': {'Hospital': '西京医院'}})
                col1.update({'Session': message.source.encode('utf-8')}, {'$set': {'Url': 'www.83215321.com'}})
                return "您选择西京医院，请输入医生姓名："
            elif news.encode('utf-8') == '2':
                col1.update({'Session': message.source.encode('utf-8')}, {'$set': {'Hospital': '西安市儿童医院'}})
                col1.update({'Session': message.source.encode('utf-8')}, {'$set': {'Url': 'book.xachyy.com'}})
                return "您选择西安市儿童医院，请输入医生姓名："
            else:
                return "请重新输入序号：\n1.西京\n2.西安市儿童医院\n3.取消挂号"
        elif trans['Doctor'] == '':
            trans = col1.find_one({'Session': message.source.encode('utf-8')})
            if trans['Url'] == 'book.xachyy.com':
                if col2.find_one({'Name': message.content.encode('utf-8')}) == None:
                    return "没有找到该医生，请重新输入医生姓名："
                else:
                    col1.update({'Session': message.source.encode('utf-8')},
                                {'$set': {'Doctor': message.content.encode('utf-8')}})
                    return "您选择医生：{}，请输入挂号时间：\n1.现在\n2.明天抢号\n3.取消挂号".format(message.content.encode('utf-8'))
            elif trans['Url'] == 'www.83215321.com':
                if col5.find_one({'Name': message.content.encode('utf-8')}) == None:
                     return "没有找到该医生，请重新输入医生姓名："
                else:
                     col1.update({'Session': message.source.encode('utf-8')},
                                 {'$set': {'Doctor': message.content.encode('utf-8')}})
                     return "您选择医生：{}，请输入挂号时间：\n1.现在\n2.明天抢号\n3.取消挂号".format(message.content.encode('utf-8'))
        elif trans['Time'] == '':
            news = message.content
            if news.encode('utf-8') == '1':
                col1.update({'Session': message.source.encode('utf-8')}, {'$set': {'Time': '现在'}})
                reply = TextReply(message=message, content='success')
                reply.process_args()
                back_message = get_verify_register(message.source.encode('utf-8'),trans['Url'])
                print 5
                return back_message

            elif news.encode('utf-8') == '2':
                col1.update({'Session': message.source.encode('utf-8')}, {'$set': {'Time': '明天'}})
                back_message = get_verify_register(message.source.encode('utf-8'),trans['Url'])
                return back_message

            else:
                return "请输入正确序号：1.现在\n2.明天抢号\n3.取消挂号"


        else:

            back_message = get_verify_register(message.source.encode('utf-8'),trans['Url'])
            print '3'
            return back_message

    else:
        task = message.content
        if "挂号" in task.encode('utf-8'):
            transaction_dict = {}
            transaction_dict['Session'] = message.source.encode('utf-8')
            transaction_dict['Task'] = '1'
            transaction_dict['Hospital'] = ''
            transaction_dict['Url'] = ''
            transaction_dict['Doctor'] = ''
            transaction_dict['Time'] = ''
            transaction_dict['Pay'] = '1'
            col1.insert(transaction_dict)
            return "请输入您要就诊的医院编号：\n1.西京医院\n2.西安市儿童医院\n3.取消挂号"
        if '查看预约' in message.content.encode('utf-8'):
            b = []
            for each in col4.find({'Session': message.source.encode('utf-8')}):
                group = each['Hospital'].encode('utf-8') + ':' + each['Doctor'].encode('utf-8')
                b.append(group)
            return '\n'.join(b)
        else:
            url = 'http://www.tuling123.com/openapi/api'
            datas = {}
            datas['key'] = '852a620fce214d28bb635e074ebb7fba'
            datas['info'] = message.content
            id = message.source
            datas['userid'] = id
            html = requests.post(url, data=datas).content
            return eval(html)['text']


robot.config['HOST'] = '172.17.76.183'
robot.config['PORT'] = 80


robot.run()