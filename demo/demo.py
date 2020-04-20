# -*- coding: UTF-8 -*-

import json
import urllib.request
from bs4 import BeautifulSoup
import re
import ssl
import pymongo

ssl._create_default_https_context = ssl._create_unverified_context


def initialize():
    mongoServer = pymongo.MongoClient(host='mongodb://127.0.0.1', port=27017)
    print ("mongoDB connect status info:",mongoServer.server_info())
    return mongoServer

def run() :

    mongoServer = initialize()

    data_list = []
    page = 1
    while page <= 2:

        url = 'https://www.qiushibaike.com/8hr/page/' + str(page)
        headers = {
            'User-Agent': 'user-agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Mobile Safari/537.36'}

        request = urllib.request.Request(url, headers=headers)
        source_code = str(urllib.request.urlopen(request).read(), 'utf-8')
        plain_text = str(source_code)  # 把页面html转为text

        soup = BeautifulSoup(plain_text, 'html.parser')

        list_scpan = soup.find_all('div', {'class': 'text-box'})
        list_H2 = soup.find_all('h2')

        i = 0
        while i < len(list_scpan):
            # print (i+1, '.' + list_H2[i].get_text().strip())
            div = list_scpan[i].get_text().strip()
            # print (div)
            i += 1
            data_list.append({'title':div})
        page += 1

    db = mongoServer.test
    print (data_list)
    result = db.titles.insert_many(data_list)
    print ("mongoDB insert data result :",result)


run()


