#/usr/bin/env python
# -*- coding: UTF-8 -*-
import requests
import re
import pytesseract
from PIL import Image

def get_verify(hospital_url):
    url = 'http://{URL}/modules/verifyImage.ashx'.format(URL=hospital_url)

    session = requests.session()

    response= session.get(url)
    response_headers = response.headers
    response_data = response.content
    file = open('/root/myproject/guahaoimage.jpg','wb')
    file.write(response_data)
    file.close()
    image = Image.open('/root/myproject/guahaoimage.jpg')
    code = pytesseract.image_to_string(image)

    session_id = ''.join(re.findall('ASP.NET_SessionId=(.*); path=/;',response_headers['Set-Cookie']))
#    code_id = ''.join(re.findall('HBHOSPITALCODE=(\d\d\d\d)',response_headers['Set-Cookie']))
    return session_id,code


hospital_url = 'www.83215321.com'
session_id,code= get_verify(hospital_url)
print session_id,code