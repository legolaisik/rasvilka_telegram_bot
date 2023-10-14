import requests
import json
import sqlite3

from sql_func import *
from config import *

MAINNET_API_BASE = "https://toncenter.com/api/v2/"
TESTNET_API_BASE = "https://testnet.toncenter.com/api/v2/"


async def detect_address(address):
    url = ''
    r = requests.get(url)
    response = json.loads(r.text)
    try:
        print(response['result']['bounceable']['b64url'])
        return response['result']['bounceable']['b64url']
    except:
        return False
