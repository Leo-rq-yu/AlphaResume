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



lfasr_host = 'https://raasr.xfyun.cn/v2/api'
# 请求的接口名
api_upload = '/upload'
api_get_result = '/getResult'

dashscope.api_key = 'sk-3c43423c9fee4af8928fd8bc647291ee'
import re
from pymongo import MongoClient
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
MONGODB_URL = "mongodb+srv://leoyuruiqing:WziECEdgjZT08Xyj@airesume.niop3nd.mongodb.net/?retryWrites=true&w=majority&appName=AIResume"
DB_NAME = "airesumedb"
COLLECTION_NAME = "resumeChats"
COLLECTION_NAME_1 = "improvedUsers"
COLLECTION_NAME_2 = "resumeAudio"
client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
collection_1 = db[COLLECTION_NAME_1]
collection_2 = db[COLLECTION_NAME_2]

priority = {
    "基础信息": {
        "简历标题": "简历标题",
        "姓名": "姓名",
        "手机号码": "手机号码",
        "邮箱": "邮箱"
    },
    "个人评价": "个人评价",
    "教育经历": {
        "学历": "学历",
        "学校名称": "学校名称",
        "起止时间": "起止时间",
        "院系": "院系",
        "专业": "专业"
    },
    "职业经历": {
        "公司名称": "公司名称",
        "城市": "城市",
        "起止时间": "起止时间",
        "职位": "职位",
        "职责": "职责"
    },
    "项目经历": {
        "项目名称": "项目名称",
        "城市": "城市",
        "起止时间": "起止时间",
        "角色": "角色",
        "项目成就": "项目成就",
        "项目描述": "项目描述",
        "项目职责": "项目职责"
    },
    "获奖与证书": {
        "奖项名称": "奖项名称",
        "获奖时间": "获奖时间",
        "颁奖机构": "颁奖机构",
        "证书名称": "证书名称",
        "颁发机构": "颁发机构",
        "取得时间": "取得时间"
    },
    "科研论文与知识产权": {
        "论文标题": "论文标题",
        "作者排序": "作者排序",
        "期刊/会议": "期刊/会议",
        "出版时间": "出版时间",
        "专利名称": "专利名称",
        "专利号": "专利号",
        "申请/授权日期": "申请/授权日期"
    },
    "技能": {
        "技能名称": "技能名称",
        "熟练度": "熟练度"
    },
    "语言": {
        "语言": "语言",
        "熟练度": "熟练度"
    }
}

chatId = sys.argv[1]
resumeId = sys.argv[2]


# chatId = 'a4e6762c-b26d-4619-92dd-2bd660adae5f'
# resumeId = 'a4e6762c-b26d-4619-92dd-2bd660adae5f'
# section_id = 1


keys_list = ['基本信息', '个人评价', '教育经历', '职业经历', '项目经历', '获奖', '证书', '语言', '技能', '科研论文', '知识产权']
initial_question_list = [
    # 基础信息
    "您能提供一下您的基本信息吗？包括姓名、联系电话、电子邮件和微信号。",

    # 个人评价
    "您可以简要描述一下自己的个人评价吗？包括您的优势、工作态度和职业目标等。",

    # 教育经历
    "您能按照学历从高到低列出您的教育背景吗？请包括以下信息：学历、学校名称、专业、城市、国家、起止时间、院系、GPA、排名、获奖记录和主修课程。",

    # 职业经历
    "请列出您的实习或工作经历，并按时间顺序提供以下信息：公司名称、城市、国家、起止时间、职位、部门及职责&业绩描述。",

    # 项目经历
    "您参与过哪些重要的项目？如果有，请按照时间顺序描述：项目名称、城市、国家、起止时间、项目链接、项目角色、项目描述、项目成就和项目职责。",

    # 获奖与证书
    "您获得过哪些奖项？如果有，请按照时间顺序列出奖项名称、颁奖机构、获奖级别、获奖时间、获奖名次和简要描述。",
    "您获得过哪些证书？如果有，请按照时间顺序列出证书名称、颁发机构、取得时间和证书详情。",

    # 语言
    "请告诉我您掌握的所有语言以及对每种语言的熟练程度，可以用以下等级划分：普通、流利、高级、母语。如果您有相关语言考试的得分或证书/资格认证，也请提供。",

    # 技能
    "您掌握哪些专业技能？请列出您熟悉的软件、工具或技术，以及相应的熟练程度。",

    # 知识论文与知识产权
    "您发表过哪些科研论文？如果有，请按照时间顺序提供论文标题、作者顺序、出版时间、期刊/会议、DOI/链接、研究描述和个人贡献。",
    "您取得过哪些知识产权？如果有，请按照时间顺序提供专利名称、专利号和申请/授权时间。",

]


# 判断是否是有效的UUID格式
def is_valid_uuid(uuid_string):
    uuid_regex = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')
    return bool(uuid_regex.match(uuid_string))


def get_chat_from_mongodb(chat_id, resume_id):
    # 假设你已经知道如何定位到特定用户的聊天记录，这里用一个示例查询

    # 查询特定用户的聊天记录
    chat_record = collection.find_one({"_id": chat_id})
    user_record = collection_1.find_one({"_id": resume_id})
    print(user_record, flush=True)
    chat_messages = chat_record['messages']

    standard_json = user_record['personal_data']
    print(standard_json, flush=True);
    # 获取最后一条消息. 格式是mock_qa.json里的格式
    last_message = chat_messages[-1]

    section_id = chat_record['sectionId']

    #print(last_message)

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
                    upload_file_path=None,
                    audio_data=audio_data
                )
                result = api.get_result()
                last_message['answer'] = result
                print("audio-to-text result", flush=True)
                print(last_message, flush=True)

            except Exception as e:
                print(f"Error during audio-to-text conversion: {e}")
                last_message['answer'] = "Error during audio-to-text conversion."

    except Exception as e:
        print(f"An error occurred: {e}")
        last_message['answer'] = "An error occurred while processing the request."



    return last_message, standard_json, section_id



def check_if_initial(json_data, section_id):
    #dict_data = json.loads(json_data)
    section_data = {}
    if section_id == 5:
        section_data = json_data['获奖与证书']['获奖']
    elif section_id == 6:
        section_data = json_data['获奖与证书']['证书']
    elif section_id == 7:
        section_data = json_data['语言']
    elif section_id == 8:
        section_data = json_data['技能']
    elif section_id == 9:
        section_data = json_data['科研论文与知识产权']['科研论文']
    elif section_id == 10:
        section_data = json_data['科研论文与知识产权']['知识产权']
    else:
        section_data = json_data[list(json_data.keys())[section_id]]

    if isinstance(section_data, dict):
        if all(value != "" for value in section_data.values()):
            return True
        return False
    elif isinstance(section_data, list):
        check_point = 0
        for item in section_data:
            # if some of the items are not empty, return False
            if any(value == "" for value in item.values()):
                check_point += 1
        if check_point == 0:
            return True
        return False
    else: # it is a string
        if section_data != "":
            return True
        return False



def ask_new_question(updated_json, key, section_id, current_key):
    prompt = (
        f"你是一个友好的面试官，正在询问求职者的个人信息。\n"
        f"现在你正在询问的是有关求职者{keys_list[section_id]}这一块的内容。\n"
        f"你注意到求职者在{keys_list[section_id]}部分下的{current_key}栏位是空的。\n"
        f"请提出一个问题，明确指出{keys_list[section_id]}部分中的{current_key}栏位需要补充信息。\n"
        f"在问题中，确保提及当前询问的板块内容和需要填写的具体信息。\n"
        f"只返回问题本身，无需添加额外的解释或说明。\n"
        f"请使用友好，轻松，和鼓励性的语气。"
    )



    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_max,
        prompt=prompt,
        seed=1234,
        top_p=0.2,
        result_format='text',
        enable_search=False,
        max_tokens=2000,
        temperature=0.1,
        repetition_penalty=1.0
    )

    if response.status_code == HTTPStatus.OK:
        #print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.


def find_all_empty(standard_json, updated_json, section_id):
    # change type of standard_json and updated_json
    #print(type(standard_json))
    #print(list(standard_json.keys())[section_id])
    section_updated = {}

    if section_id == 5:
        section_updated = updated_json['获奖与证书']['获奖']
    elif section_id == 6:
        section_updated = updated_json['获奖与证书']['证书']
    elif section_id == 7:
        section_updated = updated_json['语言']
    elif section_id == 8:
        section_updated = updated_json['技能']
    elif section_id == 9:
        section_updated = updated_json['科研论文与知识产权']['科研论文']
    elif section_id == 10:
        section_updated = updated_json['科研论文与知识产权']['知识产权']
    else:
        section_updated = updated_json[list(updated_json.keys())[section_id]]

    empty_keys = []


    if isinstance(section_updated, dict):
        for key in section_updated:
            if section_updated[key] == "":
                empty_keys.append(key)
    elif isinstance(section_updated, list):
        for i in range(len(section_updated)):
            for key in section_updated[i]:
                if section_updated[i][key] == "":
                    empty_keys.append(key)
    else:
        if section_updated == "":
            empty_keys.append(list(updated_json.keys())[section_id])

    return empty_keys, section_updated

def process_asking(json_data, section_id, standard_json):
    if section_id == 11:
        return "您的简历已经填写完毕。"
    bool_check = check_if_initial(json_data, section_id)
    print(bool_check)
    if bool_check: # if the section is already filled
        section_id += 1
        if section_id == 11:
            return "您的简历已经填写完毕。"
        # update the section_id in the chat record
        collection.update_one(
            {"_id": chatId},
            {"$set": {"sectionId": section_id}}
        )
        return initial_question_list[section_id]
    else:
        # not the initial question, get the json chat data from json
        current_key, section_new = find_all_empty(standard_json, json_data, section_id)
        print(current_key, flush=True)
        print(section_id, flush=True)
        new_question = ask_new_question(section_new, keys_list[section_id], section_id, current_key)
        return new_question


def update_json(original_json, last_chat):
    # prompt = (f"我有一段对话和一个有一部分填空的json文件。请你判断这段对话中包含的信息能填入json文件的哪里,然后更新这个json。''"
    #           f"如果对话的回答中希望跳过某一个部分，或者特别说明并无这部分的信息，请在这个部分的值中填入'无'，而不是空字符串。"
    #           f"请注意，如果问题中没有提到的键，和回答中没有特别说明并无这部分信息的键，请不要擅自填充无，而是保持为空。"
    #           f"你需要返回一个完整的json文件。不需要加任何注释。以下是对话内容：{last_chat}")
    # prompt += f"以下是json文件内容：{original_json}"

    prompt = (
        f"你是一位专业的数据分析师，你的专长在于理解对话内容并将相关信息映射到JSON结构中。\n"
        f"你将收到一段对话和一个部分已填充的JSON文件。\n"
        f"你的任务是分析这段对话，确定其中包含的信息能够填入JSON文件的哪些部分，并更新这个JSON文件。\n\n"

        f"如果对话的回答中明确指示跳过某一部分，或者特别说明并无这部分的信息，\n"
        f"请在JSON相应字段中填入'无'。\n"
        f"然而，如果某个字段在问题中没有被提及，而且回答中没有特别说明并无这部分信息，\n"
        f"则不应擅自填充'无'，而应保持该字段为空。\n\n"

        f"你需要返回一个完整的JSON文件，不需要添加任何注释。\n"
        f"以下是对话内容：\n{last_chat}\n"
        f"以下是JSON文件内容：\n{original_json}\n"
    )

    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_max,
        prompt=prompt,
        seed=1234,
        top_p=0.2,
        result_format='text',
        enable_search=False,
        max_tokens=2000,
        temperature=0.1,
        repetition_penalty=1.0
    )

    if response.status_code == HTTPStatus.OK:
        # print(response.usage)  # The usage information
        #print(response.output['text'])
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.


def extract_json(data_str):
    # 使用正则表达式找到最外层的大括号
    matches = re.search(r'{.*}', data_str, re.S)
    if matches:
        json_str = matches.group(0)
        # print(json_str)
        try:
            # 尝试解析 JSON，确保它是有效的
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError as e:
            print("找到的字符串不是有效的 JSON。",e, flush=True)
            return None
    else:
        print("没有找到符合 JSON 格式的内容。", flush=True)
        return None


def update_mongodb(chat_id, new_question, resume_id, updated_json):
    chat_record = collection.find_one({"_id": chat_id})
    resume_record = collection_1.find_one({"_id": resume_id})

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

        print(json.dumps({"status": "success", "id": messages_length + 1, "message": new_message}), flush=True)
    else:
        print(json.dumps({"status": "error", "message": "Chat record not found"}), flush=True)

    if resume_record:
        collection_1.update_one(
            {"_id": resume_id},
            {"$set": {"personal_data": updated_json}}
        )
        print(json.dumps({"status": "success", "message": "Resume record updated"}), flush=True)
    else:
        print(json.dumps({"status": "error", "message": "Resume record not found"}), flush=True)







def close_mongodb():
    client.close()


def concat_question(lastmessage, new_question):
    # first, use dashscope to generate a summary of the last message
    prompt = f"你是一个面试官，正在询问求职者的个人信息。"
    prompt += f"你刚刚问了这个问题：{lastmessage['question']}。"
    prompt += f"求职者的回答是：{lastmessage['answer']}。"
    prompt += f"现在你需要总结一下从这个问题和相应的回答中获得的信息。"
    prompt += f"你需要以面试官的口吻，用友好的语气，简洁地总结这个问题的回答。"
    prompt += f"请注意，你只需要返回总结的内容，不需要任何其他内容，比如解释。"

    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_max,
        prompt=prompt,
        seed=1234,
        top_p=0.2,
        result_format='text',
        enable_search=False,
        max_tokens=2000,
        temperature=0.1,
        repetition_penalty=1.0
    )

    if response.status_code == HTTPStatus.OK:
        #print(response.usage)  # The usage information
        #print(response.output['text'])
        summary = response.output['text']
    else:
        print(response.code)

    # then, concatenate the summary with the new question
    summary += "接下来："
    summary += new_question
    return summary






last_message, standard_json, section_id = get_chat_from_mongodb(chatId, resumeId)
json_update = update_json(standard_json, last_message)
print("json_update", flush=True)
print(json_update, flush=True)
json_update = re.sub(r"```json", '', json_update)
json_update = re.sub(r"```", '', json_update)
# json_update dtype: str
# 只保留str最外层的两个{}之内的内容，删除其他内容
json_update = extract_json(json_update)
print("json_update after extract", flush=True)
print(json_update, flush=True)
new_query = process_asking(json_update, section_id, standard_json)
final_question = concat_question(last_message, new_query)
print("resumeid", flush=True)
print(resumeId, flush=True)
update_mongodb(chatId, final_question, resumeId, json_update)
close_mongodb()
print(final_question, flush=True)
