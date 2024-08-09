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
import Search_from_db

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
    chat_record = collection.find_one({"_id": chatId})
    interview_type = chat_record['interviewType']

    resume = user_record['markdownData']
    company_info = {}
    company_info['面试公司'] = chat_record['companyName']
    company_info['岗位'] = chat_record['position']

    return resume, interview_type, company_info


def initialize_question(resume, interview_type, company_info):
    if interview_type == "技术面":
        params = "该面试的特点是对求职者的专业技能进行考察，主要考察求职者的专业技能、知识水平和解决问题的能力。"
        prompt = (
            "你是一位友好的面试官，擅长与求职者进行交流与提问。你刚刚获得了一位面试者的简历。"
            f"接下来你会与他进行一场{interview_type}的面试。"
            f"该面试的特点是{params}\n"
            f"公司和岗位信息如下：\n{company_info}\n"
            "请你按照以下步骤生成面试问题：\n"
            "1. 仔细分析面试者的简历内容，基于他的技能、经验和教育背景，判断他和岗位的契合度。\n"
            "2. 针对该岗位，提出5个与岗位要求相关的专业性技术问题，确保问题能够评估面试者在该领域的技术能力和知识水平。\n"
            "3. 根据面试者简历中提到的过往经验、学过的课程和以前的工作经历，提出与申请岗位符合的5个技术性问题。这些问题应注重目标实现过程，以判断求职者的技术是否符合该岗位的要求。\n"
            "请以Python列表的形式返回这10个问题，不需要任何其他内容。\n"
            "注意：\n"
            "- 提出的技术问题要有针对性和深度，能够揭示面试者的真实水平。\n"
            "- 挖掘简历内容的问题应基于简历中具体的项目和经验，避免泛泛而谈。\n"
            "- 行为面试问题应与岗位实际工作情境相关，具有实际操作意义。\n"
            f"以下是求职者的个人简历：\n{resume}\n"
        )
    elif interview_type == "行为面":
        params = "该面试的特点是对求职者的软技能进行考察，主要考察求职者的团队合作、沟通能力、应对压力和工作态度等方面。"
        prompt = (
            "你是一位友好的面试官，擅长与求职者进行交流与提问。你刚刚获得了一位面试者的简历。"
            f"接下来你会与他进行一场{interview_type}的面试。"
            f"该面试的特点是{params}\n"
            f"公司和岗位信息如下：\n{company_info}\n"
            "请你按照以下步骤生成面试问题：\n"
            "1. 仔细分析面试者的简历内容，基于他的技能、经验和教育背景，判断他和岗位的契合度。\n"
            "2. 提出5个与岗位相关的行为面试问题，这些问题应考察面试者在团队合作、沟通能力、应对压力和工作态度等方面的表现。\n"
            "3. 根据面试者简历中提到的过往经验、学过的课程和以前的工作经历，提出5个行为面试问题。这些问题应注重具体情境下的表现，以判断求职者在实际工作中的行为和决策能力。\n"
            "请以Python列表的形式返回这10个问题，不需要任何其他内容。\n"
            "注意：\n"
            "- 提出的行为问题要有针对性和深度，能够揭示面试者的真实表现。\n"
            "- 挖掘简历内容的问题应基于简历中具体的项目和经验，避免泛泛而谈。\n"
            "- 行为面试问题应与岗位实际工作情境相关，具有实际操作意义。\n"
            f"以下是求职者的个人简历：\n{resume}\n"
        )
    elif interview_type == "HR面":
        params = "该面试的特点是对求职者的综合素质进行考察，主要考察求职者的综合素质、文化契合度和个人发展规划等方面。"
        prompt = (
            "你是一位友好的面试官，擅长与求职者进行交流与提问。你刚刚获得了一位面试者的简历。"
            f"接下来你会与他进行一场{interview_type}的面试。"
            f"该面试的特点是{params}\n"
            f"公司和岗位信息如下：\n{company_info}\n"
            "请你按照以下步骤生成面试问题：\n"
            "1. 仔细分析面试者的简历内容，基于他的技能、经验和教育背景，判断他和岗位的契合度。\n"
            "2. 提出5个与岗位相关的HR面试问题，这些问题应考察面试者的职业动机、文化契合度、价值观以及对公司的认知。\n"
            "3. 根据面试者简历中提到的过往经验、学过的课程和以前的工作经历，提出5个HR面试问题。这些问题应注重求职者的职业发展目标、稳定性和对公司文化的适应性。\n"
            "请以Python列表的形式返回这10个问题，不需要任何其他内容。\n"
            "注意：\n"
            "- 提出的HR问题要有针对性和深度，能够揭示面试者的职业动机和价值观。\n"
            "- 挖掘简历内容的问题应基于简历中具体的项目和经验，避免泛泛而谈。\n"
            "- HR面试问题应与公司文化和岗位职责相关，确保能够评估面试者的长期适应性和稳定性。\n"
            f"以下是求职者的个人简历：\n{resume}\n"
        )
    else:
        # 此为业务面
        params = "该面试的特点是对求职者的业务能力进行考察，主要考察求职者的业务能力、解决问题的能力和创新能力等方面。"
        prompt = (
            "你是一位友好的面试官，擅长与求职者进行交流与提问。你刚刚获得了一位面试者的简历。"
            f"接下来你会与他进行一场{interview_type}的面试。"
            f"该面试的特点是{params}\n"
            f"公司和岗位信息如下：\n{company_info}\n"
            "请你按照以下步骤生成面试问题：\n"
            "1. 仔细分析面试者的简历内容，基于他的技能、经验和教育背景，判断他和岗位的契合度。\n"
            "2. 提出5个与岗位相关的业务面试问题，这些问题应考察面试者的业务理解能力、行业知识、商业敏感度以及他们如何为公司的业务目标做出贡献。\n"
            "3. 根据面试者简历中提到的过往经验、学过的课程和以前的工作经历，提出5个业务面试问题。这些问题应注重求职者在实际业务中的表现和解决实际问题的能力，以判断他们是否具备推动业务成功的潜力。\n"
            "请以Python列表的形式返回这10个问题，不需要任何其他内容。\n"
            "注意：\n"
            "- 提出的业务问题要有针对性和深度，能够揭示面试者的业务敏感度和商业理解能力。\n"
            "- 挖掘简历内容的问题应基于简历中具体的项目和经验，避免泛泛而谈。\n"
            "- 业务面试问题应与公司业务实际相关，确保能够评估面试者在实现公司业务目标中的潜力和实际贡献。\n"
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

        #print(json.dumps({"status": "success"}))
    else:
        print(json.dumps({"status": "error", "message": "Chat record not found"}))



resume, interviewtype, companyinfo = get_resume_from_mongodb(resumeId)
full_description = Search_from_db.get_company_info_from_mongodb(companyinfo)
question_list = initialize_question(resume, interviewtype, companyinfo)
#print(question_list)
update_mongodb(question_list, chatId)
client.close()






