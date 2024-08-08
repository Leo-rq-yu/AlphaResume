import json
from http import HTTPStatus
import dashscope
import time
import base64
import hashlib
import hmac
import json
import os
import time
import requests
import urllib
import re
from pymongo import MongoClient
import sys
import io
import time


def get_company_info_from_mongodb(company_info):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    MONGODB_URL = "mongodb+srv://leoyuruiqing:WziECEdgjZT08Xyj@airesume.niop3nd.mongodb.net/?retryWrites=true&w=majority&appName=AIResume"
    DB_NAME = "airesumedb"
    COLLECTION_NAME = "hiringInformation"
    client = MongoClient(MONGODB_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    company_name = company_info['面试公司']
    job_title = company_info['岗位']
    if company_name != "其他":
        company_description = collection.find_one({"companyName": company_name, "position": job_title})
        keys_to_keep = ['companyName', 'position', 'positionDescription', 'positionFunctions', 'yearsOfExperience']
        return_dict = {key: company_description[key] for key in keys_to_keep if key in company_description}

        # 更改键名
        translation_map = {
            'companyName': '面试公司',
            'position': '岗位',
            'positionDescription': '岗位描述',
            'positionFunctions': '岗位职责',
            'yearsOfExperience': '经验要求'
        }

        # 使用字典推导式同时重命名键
        return_dict = {translation_map[key]: value for key, value in return_dict.items()}
    else:
        return_dict = company_info

    return return_dict





