import requests
import aiohttp
import json
import sqlite3
import time
from fuzzywuzzy import process
import random
import re

from sql_func import *
from config import *

BASE_URL = "https://api.hh.ru/vacancies"
headers = {'HH-User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"}

async def get_recomendations(profile_id, conn: sqlite3.Connection):

    profile = await db_get_profile(profile_id, conn)
    if profile:

        params = {
            'text': profile[2]
                }
        if profile[9] != '':
            params['area'] = profile[9]
        if profile[6] != '':
            params['experience'] = profile[6]
        if profile[7] != '':
            params['employment'] = profile[7]
        if profile[8] != '':
            params['schedule'] = profile[8]
        if profile[3] != '':
            params['salary'] = profile[3]

        key_list = {}
        r = requests.get(BASE_URL, headers=headers, params=params)

        for item in r.json()['items'][:10]:

            key_r = requests.get('%s/%s' % (BASE_URL, item['id'],), headers=headers)
            for skill in key_r.json()['key_skills']:
                if skill['name'].lower() in key_list.keys():
                    key_list[skill['name'].lower()] += 1
                else:
                    key_list[skill['name'].lower()] = 1

            time.sleep(2)

        keys = []
        for key, value in key_list.items():
            if value > 1:
                keys.append(key.lower())

        for i in profile[4].split(', '):
            i = i.lower()
            true_val = process.extractOne(i, keys)
            if true_val != None:
                if (true_val[1] > 85 and len(i) < 5) or true_val[1] > 92:
                    i = true_val[0].lower()

            if i in keys:
                keys.remove(i)

        return keys
    
    else:

        return False
    
async def get_vacancies(profile_id, conn: sqlite3.Connection):

    profile = await db_get_profile(profile_id, conn)
    if profile:

        params = {
            'text': profile[2]
                }
        if profile[9] != '':
            params['area'] = profile[9]
        if profile[6] != '':
            params['experience'] = profile[6]
        if profile[7] != '':
            params['employment'] = profile[7]
        if profile[8] != '':
            params['schedule'] = profile[8]
        if profile[3] != '':
            params['salary'] = profile[3]

        key_list = {}
        r = requests.get(BASE_URL, headers=headers, params=params)

        item = random.choice(r.json()['items'])

        role = item['name']
        company = item['employer']['name']
        try:
            salary = str(item['salary']['to'])
        except:
            salary = '?'
        descr = item['snippet']['responsibility']
        link = item['alternate_url']

        answer = '''Должность %s от компании %s
Зарплата до %s
Описание: %s 
Посмотреть подробнее: %s''' % (role, company, salary, descr, link)
        
        return re.sub('<.*?>', '', answer)
    
    else:

        return False