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

from kimi_model import kimi_generate

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
COLLECTION_NAME = "resumeChats"
COLLECTION_NAME_1 = "improvedUsers"
COLLECTION_NAME_2 = "resumeAudios"
client = MongoClient(MONGODB_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
collection_1 = db[COLLECTION_NAME_1]
collection_2 = db[COLLECTION_NAME_2]


chatId = sys.argv[1]
resumeId = sys.argv[2]


# chatId = 'a4e6762c-b26d-4619-92dd-2bd660adae5f'
# resumeId = 'a4e6762c-b26d-4619-92dd-2bd660adae5f'
# section_id = 1


keys_list = ['基本信息', '个人评价', '教育经历', '职业经历', '项目经历', '获奖', '证书', '语言', '技能', '科研论文', '知识产权']


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

    standard_json = user_record['personal_data']

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



    return last_message, standard_json





def update_json(original_json, last_chat):
    prompt = (
        f"你是一位专业的数据分析师，专长在于解析对话内容并将相关信息映射到JSON结构中。\n"
        f"你将收到一段对话和一个部分已填充的JSON文件。\n"
        f"你的任务是：\n"
        f"1. 分析对话内容。\n"
        f"2. 确定对话中包含的信息可以填入JSON文件的哪些部分。\n"
        f"3. 更新并返回完整的JSON文件。\n\n"

        f"注意事项：\n"
        f"- 如果对话中明确指示跳过某一部分或特别说明并无这部分信息，请在JSON相应字段中填入'无'。\n"
        f"- 如果某个字段在问题中没有被提及且回答中没有特别说明并无这部分信息，则保持该字段为空。\n"
        f"- 返回的JSON文件中，所有的key和value都需使用双引号。\n\n"

        f"以下是对话内容：\n{last_chat}\n"
        f"以下是部分已填充的JSON文件内容：\n{original_json}\n"
    )

    response = kimi_generate(prompt)
    return response


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
            print("找到的字符串不是有效的 JSON。",e)
            return None
    else:
        print("没有找到符合 JSON 格式的内容。")
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

        print(json.dumps({"status": "success", "id": messages_length + 1, "message": new_message}))
    else:
        print(json.dumps({"status": "error", "message": "Chat record not found"}))

    if resume_record:
        collection_1.update_one(
            {"_id": resume_id},
            {"$set": {"personal_data": updated_json}}
        )
        print(json.dumps({"status": "success", "message": "Resume record updated"}))
    else:
        print(json.dumps({"status": "error", "message": "Resume record not found"}))



def process_asking(json_str):
    prompt = (
        "你是一位语气友好的面试官，擅长与求职者进行沟通与交流。"
        "我将提供给你一份面试者填写的JSON格式的个人信息，我希望你能向求职者就其个人信息的完整性做出反馈。"
        "请你按照以下步骤生成反馈内容： \n"
        "1. 检查整个JSON文件，找出所有value为'\'的key，这些key即为求职者为填写的信息。 \n"
        "2. 采用鼓励与支持的语气，根据未完成的信息在JSON格式中所属的部分分段落向求职者提示未完成的信息。 \n"
        "3. 在每一个段落中，应该首先指出求职者未完成的信息有哪些，再分析这些信息对简历与求职的作用，最后指导求职者该如何补充这部分信息。 \n"
        "4. 在向求职者提示完未填写的信息后，根据你作为面试官的专业知识，提示未填写的信息中哪些信息对于简历是至关重要的，建议求职者优先完善这部分信息。 \n"
        "5. 输出你对于求职者的反馈。 \n"
        "注意事项： \n"
        "- 如果你发现求职者的个人信息json中某个部分的信息大量缺失，则不需要将该部分所有信息缺失的key列出来，而是直接提示求职者该部分的一级key。 \n"
        "- 如果某些字段的value为'无'，这表明求职者已经回答了相关问题，因此不需要再次询问。 \n"
        "- 注意向求职者反馈的语气，采用亲切、鼓励、支持的语气，让求职者在轻松的状态下进行沟通。 \n"
        f"以下是求职者的个人信息JSON：\n{json_str}\n"
    )
    try:
        response = kimi_generate(prompt)
        if not response:
            raise ValueError("Received empty response from generate_response.")
        return response
    except Exception as e:
        print(f"Error during process_asking: {e}")
        return None





def concat_question(lastmessage, new_question):
    # first, use dashscope to generate a summary of the last message
    prompt = f"你是一个面试官，正在询问求职者的个人信息。"
    prompt += f"你刚刚问了这个问题：{lastmessage['question']}。"
    prompt += f"求职者的回答是：{lastmessage['answer']}。"
    prompt += f"现在你需要总结一下从这个问题和相应的回答中获得的信息。"
    prompt += f"你需要以面试官的口吻，用友好的语气，简洁地总结这个问题的回答。"
    prompt += f"请注意，你只需要返回总结的内容，不需要任何其他内容，比如解释。"

    summary = kimi_generate(prompt)

    # then, concatenate the summary with the new question
    summary += "接下来："
    summary += new_question
    return summary




def close_mongodb():
    client.close()




# get start time
start_time = time.time()
last_message, standard_json = get_chat_from_mongodb(chatId, resumeId)
json_update = update_json(standard_json, last_message)
print(json_update)
json_update = re.sub(r"```json", '', json_update)
json_update = re.sub(r"```", '', json_update)
# json_update dtype: str
# 只保留str最外层的两个{}之内的内容，删除其他内容
json_update = extract_json(json_update)
new_query = process_asking(json_update)
# get end time, if within 1 minute, wait until 1 minute
end_time = time.time()
if end_time - start_time < 60:
    time.sleep(60 - (end_time - start_time))

final_question = concat_question(last_message, new_query)
print(final_question)
update_mongodb(chatId, final_question, resumeId, json_update)
close_mongodb()
print(new_query)