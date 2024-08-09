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
import Search_from_db

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

# 判断是否是有效的UUID格式
def is_valid_uuid(uuid_string):
    uuid_regex = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')
    return bool(uuid_regex.match(uuid_string))


def get_chat_from_mongodb(chat_id, resume_id):
    # 假设你已经知道如何定位到特定用户的聊天记录，这里用一个示例查询

    # 查询特定用户的聊天记录
    chat_record = collection.find_one({"_id": chat_id})
    user_record = collection_1.find_one({"_id": resume_id})

    chat_messages = chat_record['messages']

    question_list = chat_record['question_list']

    resume = user_record['markdownData']

    # 获取最后一条消息. 格式是mock_qa.json里的格式
    last_message = chat_messages[-1]

    print(last_message)

    last_answer = last_message['answer']
    # check if it is an id, ie, no chinese characters
    try:
        if is_valid_uuid(last_answer):
            audio_id = last_answer
            audio_record = collection_2.find_one({"_id": audio_id})

            if audio_record is None:
                raise ValueError("No audio record found for the given UUID.")

            audio_data = audio_record['audio']  # assuming this is a .wav file

            try:
                # Convert the audio to text
                api = audio_to_text.RequestApi(
                    appid="80922260",
                    secret_key="84268ea312aee377ace0b8468633bd0a",
                    upload_file_path=audio_record['audio']
                )
                result = api.get_result()
                last_message['answer'] = result

            except Exception as e:
                print(f"Error during audio-to-text conversion: {e}")
                last_message['answer'] = "Error during audio-to-text conversion."

    except Exception as e:
        print(f"An error occurred: {e}")
        last_message['answer'] = "An error occurred while processing the request."

#xuyaoxiugai
    company_info = {}
    company_info['面试公司'] = chat_record['company']
    company_info['岗位'] = chat_record['position']



    return last_message, resume, question_list, company_info


def update_question_list(chat_id, last_qa, question_list):
    prompt = (
        "你是一位友好的面试官，擅长与求职者进行交流与提问。现在你获得了上一个你提出的问题。"
        "请你按照以下步骤更新备选问题列表：\n"
        "1. 从备选问题列表中删除上一个你提出的问题。\n"
        "2. 返回更新后的备选问题列表。\n"
        "注意：\n"
        "- 只需要删除，不能修改任何格式。\n"
        f"以下是上一个你提出的问题：\n{last_qa['question']}\n"
        f"以下是备选问题列表：\n{question_list}\n"
    )

    response = generate_response(prompt)

    chat_record = collection.find_one({"_id": chat_id})

    if chat_record:

        # Add the new message to the messages array
        collection.update_one(
            {"_id": chat_id},
            {"$push": {"question_list": response}}
        )

        print(json.dumps({"status": "success"}))
    else:
        print(json.dumps({"status": "error", "message": "Chat record not found"}))



def summarize_and_ask(resume, last_qa, question_list, company_info=None):

    prompt = (
        "你是一位友好的面试官，擅长与求职者进行交流与提问。现在你正与面试者进行HR面试。\n"
        "该面试的特点是对求职者的综合素质进行考察，主要考察求职者的综合素质、文化契合度和个人发展规划等方面。"
        f"该面试者申请的公司信息及岗位信息如下：{company_info}\n"
        "现在你获得了上一个问题的对话记录，包括你提出的问题和面试者的回答。请你按照以下步骤生成下一段面试交流内容：\n"
        "1. 适当总结面试者的回答，给予鼓励和支持。\n"
        "2. 判断上一个面试问题是否需要继续追问。如果需要，请提出一个追问的问题，并将这个问题与步骤1结合在一起。\n"
        "3. 如果不需要追问，请从以下备选问题列表中选出一个适合作为下一个面试题，并将这个问题与步骤1结合在一起。\n"
        f"备选问题列表：{question_list}\n"
        f"用户简历：\n{resume}\n"
        "请以完整的段落形式返回结合后的面试交流内容，不需要返回任何其他内容。\n"
        "注意：\n"
        "- 总结反馈时要具体，引用面试者的回答要点，并给予积极的评价。\n"
        "- 追问问题要有针对性，旨在深入了解面试者的回答。\n"
        "- 选择下一个问题时要考虑整体面试流程的连贯性和逻辑性。\n"
        f"以下是上一个问题的对话记录：\n{last_qa}\n"
    )

    response = generate_response(prompt)
    return response




def update_mongodb(chat_id, new_question):
    chat_record = collection.find_one({"_id": chat_id})

    if chat_record:
        # Get the current length of the messages array
        messages_length = len(chat_record.get('messages', []))

        # Create the new message with id and question
        new_message = {"id": messages_length + 1, "question": new_question}

        # Add the new message to the messages array
        collection.update_one(
            {"_id": chat_id},
            {"$push": {"messages": new_message}}
        )

        print(json.dumps({"status": "success", "id": messages_length + 1, "message": new_message}))
    else:
        print(json.dumps({"status": "error", "message": "Chat record not found"}))




def close_mongodb():
    client.close()






resume, last_qa, question_list, company_info = get_chat_from_mongodb(chatId, resumeId)
update_question_list(chatId, last_qa, question_list)
full_company_information = Search_from_db.get_company_info_from_mongodb(company_info)
new_question = summarize_and_ask(resume, last_qa, question_list, full_company_information)
update_mongodb(chatId, new_question)
close_mongodb()