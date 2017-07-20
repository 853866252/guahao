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
import lxml.html
import datetime
robot = werobot.WeRoBot(token='ce1Jcs')

client = pymongo.MongoClient(host='172.17.76.183', port=27017)
database1 = client.Register
database2 = client.xachyy_DBS
col1 = database1.Transaction
col2 = database2.doctor_info
col3 = database1.Patient_info
col4 = database1.Transaction_plan

def get_source(url):
    session = requests.session()
    source = session.get(url).content
    return source.decode('utf-8')

def get_verify(hospital_url):
    url = 'http://{URL}/modules/verifyImage.ashx'.format(URL=hospital_url)
    session = requests.session()
    response_headers = session.get(url).headers
    session_id = ''.join(re.findall('ASP.NET_SessionId=(.*); path=/;',response_headers['Set-Cookie']))
    code_id = ''.join(re.findall('HBHOSPITALCODE=(\d\d\d\d)',response_headers['Set-Cookie']))
    return session_id,code_id

def get_patientId(weixin_session,session_id,code_id,indentify_id,password,hospital_url):
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

def get_book_time(html):
    date_time = {}
    dt_time = lxml.html.document_fromstring(html)
    doctor_date = dt_time.xpath('//img/@onclick')
    for each in doctor_date:
        time = each.split('\',\'')
        date_time['Date'] = time[1]
        date_time['Time'] = time[3]
        break
    return date_time

def get_book_items(doctor_info):

    date1 = str(datetime.date.today().replace(day=1))
    date2 = str(datetime.date.today().replace(day=1) - datetime.timedelta(-31))
    datelist = [date1,date2]
    date_time = {}
    for each in datelist:
        url = 'http://book.xachyy.com/Doctor/ajax.aspx?param=GetBookInfoByDoctorId&uimode=1&clinicLabelId='+doctor_info['ClinicLabelId'].encode("utf-8")+'&cliniclabeltype=2&clinicweektype=0&rsvmodel=1&doctorid='+doctor_info['DoctorID'].encode("utf-8")+'&selectTime='+each
        html = get_source(url)
        date_time = get_book_time(html)
        if date_time != {}:
            break
    return date_time


def register(patient_info,doctor_info,date_time):
    url = 'http://book.xachyy.com/Doctor/ajax.aspx?param=order&hospitalId=61010021&patientId={patientid}&clinicLabelId='.format(patientid=patient_info['Accoutid'])+doctor_info['ClinicLabelId'].encode("utf-8")+'&clinicDate='+date_time['Date']+'&timePartType=1&timePart='+date_time['Time']+'&channcelType=3&rsvmodel=1&returnVisitId=1'
    session = requests.Session()
    html = session.post(url).content
    return html

def get_verify_register(session):
    if col3.find_one({'Session': session}) == None:
        return "请按照如下格式进行登录验证，（登录/用户名/密码），此登录仅需一次,若没有账号请先到官网注册"
    else:
        task = col1.find_one({'Session': session})
        if task['Time'].encode('utf-8') == '现在' and task['Hospital'].encode('utf-8') == '西安市儿童医院':
            doctor_info = col2.find_one({'Name': task['Doctor']})
            patientinfo = col3.find_one({'Session': session})
            date_time = get_book_items(doctor_info)
            print date_time
            print type(date_time)
            if date_time != {}:
                back = register(patientinfo, doctor_info, date_time)
                col1.delete_one({'Session': session})
                return back
            else:
#                col1.delete_one({'Session': session})
                print '1'
                return "挂号没有开始或者已经预定完！\n请输入3取消预约该预约流程。\n\n您也可以选择其他医生或者选择明日抢号"
        elif task['Time'].encode('utf-8') == '现在' and task['Hospital'].encode('utf-8') == '西京':
            pass
        else:

            col4.insert(task)
            col1.delete_one({'Session': session})
            return "已经准备明天为您抢号，请耐心等待"




@robot.subscribe
def intro(message):
    return "欢迎来到任式机器，公众号提供自动预定挂号及抢号服务。预想挂号请输入：挂号（目前仅支持西安市儿童医院）"



@robot.text
def hello(message, session):

    trans = col1.find_one({'Session':message.source.encode('utf-8')})

    if trans != None:
        news = message.content
        task = news.split('/')
        if task[0].encode('utf-8') == '登录':
            hospital_url = trans['Url']
            session_id, code_id = get_verify(hospital_url)
            identify_id = task[1].encode('utf-8')
            password = hashlib.md5(task[2].encode('utf-8')).hexdigest()
            back = get_patientId(message.source,session_id, code_id, identify_id, password,hospital_url)
            return back+"\n请输入确定，完成任务下达"
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

            if col2.find_one({'Name': message.content.encode('utf-8')}) == None:
                return "没有找到该医生，请重新输入医生姓名："
            else:
                col1.update({'Session': message.source.encode('utf-8')},
                            {'$set': {'Doctor': message.content.encode('utf-8')}})
                return "您选择医生：{}，请输入挂号时间：\n1.现在\n2.明天抢号\n3.取消挂号".format(message.content.encode('utf-8'))
        elif trans['Time'] == '':
            news = message.content
            if news.encode('utf-8') == '1':
                col1.update({'Session': message.source.encode('utf-8')}, {'$set': {'Time': '现在'}})
                back_message = get_verify_register(message.source.encode('utf-8'))
                print '2'
                print back_message
                return back_message

            elif news.encode('utf-8') == '2':
                col1.update({'Session': message.source.encode('utf-8')}, {'$set': {'Time': '明天'}})
                back_message = get_verify_register(message.source.encode('utf-8'))
                return back_message

            else:
                return "请输入正确序号：1.现在\n2.明天抢号\n3.取消挂号"
        else:

            back_message = get_verify_register(message.source.encode('utf-8'))
            print '3'
            print back_message
            return back_message
    elif '查看预约' in message.content.encode('utf-8'):
        b = []
        for each in col4.find({'Session': message.source.encode('utf-8')}):
            group = each['Hospital'].encode('utf-8')+':'+each['Doctor'].encode('utf-8')
            b.append(group)
        return '\n'.join(b)

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
            return "请输入您要就诊的医院编号：\n1.西京\n2.西安市儿童医院\n3.取消挂号"
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