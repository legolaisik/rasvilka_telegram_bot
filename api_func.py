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
THEBURL = 'https://api.theb.ai/v1/chat/completions'
theb_headers = {'Authorization': theb_token, 'Content-Type': 'application/json'}

employment_list = [
    {
        "id": "full",
        "name": "Полная занятость"
    },
    {
        "id": "part",
        "name": "Частичная занятость"
    },
    {
        "id": "project",
        "name": "Проектная работа"
    },
    {
        "id": "volunteer",
        "name": "Волонтерство"
    },
    {
        "id": "probation",
        "name": "Стажировка"
    }
]
    
schedule_list = [
    {
        "id": "fullDay",
        "name": "Полный день"
    },
    {
        "id": "shift",
        "name": "Сменный график"
    },
    {
        "id": "flexible",
        "name": "Гибкий график"
    },
    {
        "id": "remote",
        "name": "Удаленная работа"
    },
    {
        "id": "flyInFlyOut",
        "name": "Вахтовый метод"
    }
]

education_level_list = [
    {
        "id": "secondary",
        "name": "Среднее"
    },
    {
        "id": "special_secondary",
        "name": "Среднее специальное"
    },
    {
        "id": "unfinished_higher",
        "name": "Неоконченное высшее"
    },
    {
        "id": "higher",
        "name": "Высшее"
    },
    {
        "id": "bachelor",
        "name": "Бакалавр"
    },
    {
        "id": "master",
        "name": "Магистр"
    },
    {
        "id": "candidate",
        "name": "Кандидат наук"
    },
    {
        "id": "doctor",
        "name": "Доктор наук"
    }
]

expirience_list = [
    {
        "id": "noExperience",
        "name": "Нет опыта"
    },
    {
        "id": "between1And3",
        "name": "От 1 года до 3 лет"
    },
    {
        "id": "between3And6",
        "name": "От 3 до 6 лет"
    },
    {
        "id": "moreThan6",
        "name": "Более 6 лет"
    }
]


async def get_skills(role):
    
    params = {
        'text': role
            }

    key_list = {}
    r = requests.get(BASE_URL, headers=headers, params=params)

    for item in r.json()['items'][:10]:

        key_r = requests.get('%s/%s' % (BASE_URL, item['id'],), headers=headers)
        for skill in key_r.json()['key_skills']:
            if skill['name'].lower() in key_list.keys():
                key_list[skill['name'].lower()] += 1
            else:
                key_list[skill['name'].lower()] = 1

    keys = []
    for key, value in key_list.items():
        if value > 1:
            keys.append(key.lower())

    return keys if len(keys) > 0 else False

async def get_recomendations(user_id, conn: sqlite3.Connection):

    profile = await db_get_profile(user_id, conn)
    if profile:

        for i in expirience_list:
            if i['name'] == profile[6]:
                expirience = i['id']

        for i in employment_list:
            if i['name'] == profile[8]:
                employment = i['id']

        for i in schedule_list:
            if i['name'] == profile[7]:
                schedule = i['id']

        for i in education_level_list:
            if i['name'] == profile[5]:
                education_level = i['id']

        params = {
            'text': profile[2]
                }
        if profile[9] != '':
            params['area'] = profile[9]
        if profile[6] != '':
            params['experience'] = expirience
        if profile[7] != '':
            params['employment'] = employment
        if profile[8] != '':
            params['schedule'] = schedule
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

        vacancy1 = await get_vacancies(user_id, conn, by_keys = profile[4])
        
        prompt = """Предложи должность, которую я мог бы занять сейчас с учетом этих навыков: %s. А также предложи несколько путей развития карьеры: какие должности можно занять через пару лет и что для этого нужно""" % profile[4]

        thebparams = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                    "role": "user",
                    "content": prompt
                    }
                ],
                "stream": False
                }
        
        vacancy2 = await get_vacancies(user_id, conn)

        r = requests.post(THEBURL, data = json.dumps(thebparams), headers = theb_headers)
        answer = r.json()['choices'][0]['message']['content']

        return keys, vacancy1, answer, vacancy2
        
    else:

        return False, False, False, False
    
async def get_vacancies(user_id, conn: sqlite3.Connection, by_keys = False):

    profile = await db_get_profile(user_id, conn)
    if profile:

        for i in expirience_list:
            if i['name'] == profile[6]:
                expirience = i['id']

        for i in employment_list:
            if i['name'] == profile[8]:
                employment = i['id']

        for i in schedule_list:
            if i['name'] == profile[7]:
                schedule = i['id']

        for i in education_level_list:
            if i['name'] == profile[5]:
                education_level = i['id']

        if not by_keys:

            params = {
                'text': profile[2]
                    }
            if profile[9] != '':
                params['area'] = profile[9]
            if profile[6] != '':
                params['experience'] = expirience
            if profile[7] != '':
                params['employment'] = employment
            if profile[8] != '':
                params['schedule'] = schedule
            if profile[3] != '':
                params['salary'] = profile[3]

        else:

            params = {
                'text': by_keys
            }
            if profile[9] != '':
                params['area'] = profile[9]
            if profile[6] != '':
                params['experience'] = expirience
            if profile[7] != '':
                params['employment'] = employment
            if profile[8] != '':
                params['schedule'] = schedule

        key_list = {}
        r = requests.get(BASE_URL, headers=headers, params=params)

        try:
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
        
        except:

            answer = '''Извините( Конкретную вакансию мы не нашли...'''
            
            return answer
    
    else:

        return False