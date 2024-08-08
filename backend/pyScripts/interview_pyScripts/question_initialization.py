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
import audio_to_text

from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

from qwen_model import generate_response


lfasr_host = 'https://raasr.xfyun.cn/v2/api'
# 请求的接口名
api_upload = '/upload'
api_get_result = '/getResult'

dashscope.api_key = 'sk-3c43423c9fee4af8928fd8bc647291ee'
import re
from pymongo import MongoClient
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
MONGODB_URL = "mongodb+srv://leoyuruiqing:WziECEdgjZT08Xyj@airesume.niop3nd.mongodb.net/?retryWrites=true&w=majority&appName=AIResume"
DB_NAME = "airesumedb"
COLLECTION_NAME = "interviewChats"
COLLECTION_NAME_1 = "resumeHistories"
COLLECTION_NAME_2 = "inteviewAudios"
client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
collection_1 = db[COLLECTION_NAME_1]
collection_2 = db[COLLECTION_NAME_2]



chatId = sys.argv[1]
resumeId = sys.argv[2]




def get_resume_from_mongodb(resume_id):

    user_record = collection_1.find_one({"_id": resume_id})

    resume = user_record['markdownData']

    return resume


def initialize_question(resume):
    prompt = (
        "你是一位友好的面试官，擅长与求职者进行交流与提问。你刚刚获得了一位面试者的简历。"
        "请你按照以下步骤生成面试问题：\n"
        "1. 仔细分析面试者的简历内容，基于他的技能、经验和教育背景，判断他最适合的岗位。\n"
        "2. 针对该岗位，提出5个与岗位要求相关的专业性技术问题，确保问题能够评估面试者在该领域的技术能力和知识水平。\n"
        "3. 根据面试者简历中提到的过往经验、学过的课程和以前的工作经历，提出5个深入挖掘简历内容的问题。这些问题应关注具体项目、职责、挑战和成果，目的是进一步了解面试者的实际操作能力和解决问题的能力。\n"
        "4. 根据他申请的岗位，提出5个行为面试问题，这些问题应该围绕团队合作、沟通能力、应对压力和工作态度等方面，评估面试者的软技能和文化契合度。\n"
        "请以Python列表的形式返回这15个问题，不需要任何其他内容。\n"
        "注意：\n"
        "- 提出的技术问题要有针对性和深度，能够揭示面试者的真实水平。\n"
        "- 挖掘简历内容的问题应基于简历中具体的项目和经验，避免泛泛而谈。\n"
        "- 行为面试问题应与岗位实际工作情境相关，具有实际操作意义。\n"
        f"以下是求职者的个人简历：\n{resume}\n"
    )


    response = generate_response(prompt)
    return response





def update_mongodb(question_list, chat_id):
    chat_record = collection.find_one({"_id": chat_id})

    if chat_record:

        # Add the new message to the messages array
        collection.update_one(
            {"_id": chat_id},
            {"$push": {"question_list": question_list}}
        )

        print(json.dumps({"status": "success"}))
    else:
        print(json.dumps({"status": "error", "message": "Chat record not found"}))



resume = get_resume_from_mongodb(resumeId)
question_list = initialize_question(resume)
print(question_list)
update_mongodb(question_list, chatId)
client.close()






