#/usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
import lxml
import lxml.html
import pymongo
import re
import datetime
import urllib
import urllib2
from multiprocessing.dummy import Pool

user = '622526198705312025'
password = 'liyang123!@#'


def get_source(url):
    session = requests.session()
    source = session.get(url).content
    return source.decode('utf-8')

def get_departmentid():
    url = 'http://book.xachyy.com/DepartmentList.aspx'
    source = get_source(url)
#    print html.decode('utf-8')
    selector = lxml.html.document_fromstring(source)
    dt_list = selector.xpath('//dt/a/@href')
#    print dt_list
    return dt_list

def get_doctor_list(dt_list):
    doctor_list = []
    url = 'http://book.xachyy.com/{}'
#    print dt_list
    for each in dt_list:
        a = url.format(each)
        source = get_source(a)
#        print source
        for each in get_every_doctorlist(source):
            each = each.replace('../','')
            doctor_list.append(each)
    return doctor_list

def get_every_doctorlist(source):
    doctor_Dict_list = []
    selector = lxml.html.document_fromstring(source)

    doctor_list = selector.xpath('//ul[@id="show1"]')
    for each in doctor_list:
        list = each.xpath('li/a/@href')
        for each in list:
            doctor_Dict_list.append(each)
    return doctor_Dict_list


def get_doctor_Dict(doctor_list):
    url = 'http://book.xachyy.com/{}'
    doctor_Dict = {}
    url_list = url.format(doctor_list)
    dt_source = get_source(url_list)
    dt_selector = lxml.html.document_fromstring(dt_source)
    DoctorID = re.findall('id=(................)', url_list)
    Department = dt_selector.xpath('//span[@id="LeftDocContent1_depName"]/text()')
    Name = dt_selector.xpath('//span[@id="LeftDocContent1_docName"]/text()')
    Sex = dt_selector.xpath('//span[@id="LeftDocContent1_lbSex"]/text()')
    TitleName = dt_selector.xpath('//span[@id="LeftDocContent1_TitleName"]/text()')
    clinicLabelId = re.findall('clinicLabelId=(.*)&cliniclabeltype', dt_source)
#    print ''.join(Department)
#    print ''.join(Name)
#    print ''.join(Sex)
#    print ''.join(TitleName)
#    print clinicLabelId[0]
#    print DoctorID[0]
    doctor_Dict['Department'] = ''.join(Department)
    doctor_Dict['Name'] = ''.join(Name)
    doctor_Dict['Sex'] = ''.join(Sex)
    doctor_Dict['TitleName'] = ''.join(TitleName)
    doctor_Dict['ClinicLabelId'] = clinicLabelId[0]
    doctor_Dict['DoctorID'] = DoctorID[0]
    return doctor_Dict
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
#    items = re.findall('onclick=loading\((.*)\) src=\'/Skins/Default/Images/',html,re.S)
 #   for each in items:
#        print each
    #print items




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




if __name__ == '__main__':
    n = 1
    while n:
        print ('1.爬取医生信息\n2.输入预定医生信息\n3.推出')
        n = input('please input number:')
        if n == 1:
            client = pymongo.MongoClient()
            database = client.xachyy_DBS
            col = database.doctor_info
            dt_list = get_departmentid()
            #dt_list = 'Doctor/Index.aspx?id=6101002110268008'
            doctor_list = get_doctor_list(dt_list)
            pool = Pool(20)
            results = pool.map(get_doctor_Dict,doctor_list)
            for each in results:
                col.insert(each)

        elif n == 2:
            name = raw_input('请输入您要挂的医生：')
#            nam ＝ input('请输入您要挂的医生')
            client = pymongo.MongoClient()
            database = client.xachyy_DBS
            col = database.doctor_info
            doctor_name = col.find({'Name':name})

            for each in doctor_name:
#                print each
                doctor_info = each
  #          print doctor_info
            date_time = get_book_items(doctor_info)
            register(doctor_info,date_time)

        elif n == 3:
            break





