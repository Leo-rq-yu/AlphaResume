import sys

from pymongo import MongoClient
import requests
from markdownify import markdownify as md
import os
import json
from http import HTTPStatus
import dashscope
import time
import re

dashscope.api_key = 'sk-3c43423c9fee4af8928fd8bc647291ee'

# get resume_history_id from command line
resume_history_id = sys.argv[1]
# get resume_id from command line
improved_user_id = sys.argv[2]





def get_pdf_from_mongodb(resumehist_id):
    mongo_uri = "mongodb+srv://leoyuruiqing:WziECEdgjZT08Xyj@airesume.niop3nd.mongodb.net/?retryWrites=true&w=majority&appName=AIResume"
    database_name = "airesumedb"
    collection_name = "resumeHistories"

    # 连接到MongoDB
    client = MongoClient(mongo_uri)
    db = client[database_name]
    collection = db[collection_name]

    # 查询特定用户的聊天记录
    resume_hist = collection.find_one({"_id": resumehist_id})

    # 需要修改代码：同一个useraccount有多个聊天记录，拿取最后一条记录
    # 初始化一个空字典来存储问题和答案
    md_data = resume_hist['markdownData']
    # print(md_data)

    client.close()
    return md_data


# 从本地读取json模板
template = {
    "基础信息": {
        "姓": "",
        "名": "",
        "手机号码": "",
        "邮箱": "",
        "微信号": ""
    },
    "教育经历": [
        {
            "学校名称": "",
            "专业": "",
            "城市": "",
            "国家": "",
            "起止时间": "",
            "学历": "",
            "院系": "",
            "GPA": "",
            "排名": "",
            "获奖记录": "",
            "主修课程": ""
        },
        {
            "学校名称": "",
            "专业": "",
            "城市": "",
            "国家": "",
            "起止时间": "",
            "学历": "",
            "院系": "",
            "GPA": "",
            "排名": "",
            "获奖记录": "",
            "主修课程": ""
        }
    ],
    "职业经历": [
        {
            "公司名称": "",
            "城市": "",
            "国家": "",
            "起止时间": "",
            "职位": "",
            "部门": "",
            "职责/业绩描述": ""
        },
        {
            "公司名称": "",
            "城市": "",
            "国家": "",
            "起止时间": "",
            "职位": "",
            "部门": "",
            "职责/业绩描述": ""
        }
    ],
    "项目经历": [
        {
            "项目名称": "",
            "城市": "",
            "国家": "",
            "起止时间": "",
            "项目链接": "",
            "项目角色": "",
            "项目描述": "",
            "项目成就": "",
            "项目职责": ""
        },
        {
            "项目名称": "",
            "城市": "",
            "国家": "",
            "起止时间": "",
            "项目链接": "",
            "项目角色": "",
            "项目描述": "",
            "项目成就": "",
            "项目职责": ""
        }
    ],
    "获奖与证书": {
        "获奖": [
            {
                "奖项名称": "",
                "颁奖机构": "",
                "获奖级别": "",
                "获奖时间": "",
                "获奖名次": "",
                "描述": ""
            },
            {
                "奖项名称": "",
                "颁奖机构": "",
                "获奖级别": "",
                "获奖时间": "",
                "获奖名次": "",
                "描述": ""
            }
        ],
        "证书": [
            {
                "证书名称": "",
                "颁发机构": "",
                "取得时间": "",
                "证书详情": ""
            },
            {
                "证书名称": "",
                "颁发机构": "",
                "取得时间": "",
                "证书详情": ""
            }
        ]
    },
    "语言": [
        {
            "语言": "",
            "证书/资格认证": "",
            "熟练度": "",
            "成绩": ""
        },
        {
            "语言": "",
            "证书/资格认证": "",
            "熟练度": "",
            "成绩": ""
        }
    ],
    "技能": [
        {
            "技能名称": "",
            "熟练度": ""
        },
        {
            "技能名称": "",
            "熟练度": ""
        },
        {
            "技能名称": "",
            "熟练度": ""
        },
        {
            "技能名称": "",
            "熟练度": ""
        },
        {
            "技能名称": "",
            "熟练度": ""
        }
    ],
    "科研论文与知识产权": {
        "科研论文": [
            {
                "论文标题": "",
                "作者顺序": "",
                "出版时间": "",
                "期刊/会议": "",
                "DOI/链接": "",
                "研究描述": "",
                "个人贡献": ""
            },
            {
                "论文标题": "",
                "作者顺序": "",
                "出版时间": "",
                "期刊/会议": "",
                "DOI/链接": "",
                "研究描述": "",
                "个人贡献": ""
            }
        ],
        "知识产权": [
            {
                "专利名称": "",
                "专利号": "",
                "申请/授权时间": "",
                "描述": ""
            },
            {
                "专利名称": "",
                "专利号": "",
                "申请/授权时间": "",
                "描述": ""
            }
        ]
    },
    "个人评价": ""
}


def transform_chat_json(md_data):
    prompt = f"我有一个个人简历的md版本，还有一个模式规整的json的key。这个json的value是空缺的，我需要你把md文件中的信息填入json格式的value中。" \
             f"你返回的数据是json格式，一定不需要除了json的其他内容。" \
             f"如果需要填充的内容为时间，那么请填充为'yyyy-mm-dd'这种格式。" \
             f"如果是至今，请填充为yyyy-mm-至今。" \
             f"如果范例中有的内容没有在md里找到，请储存空值。md简历： "
    # 把md转换成json, 用于填充
    md_data = md(md_data)
    prompt += md_data
    prompt += "\n json格式："
    prompt += str(template)

    response = dashscope.Generation.call(
        model='qwen-max-longcontext',
        prompt=prompt,
        seed=1234,
        top_p=0.2,
        result_format='json',
        enable_search=False,
        max_tokens=2000,
        temperature=0.1,
        repetition_penalty=1.0
    )
    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.



# 此处需要修改
md_data = get_pdf_from_mongodb(resume_history_id)
print(md_data)
# 去掉所有除了中文，英文，数字和'-', ' ', '.', '\n'之外的字符
md_data = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\- \n]', '', md_data)
# save md_data to a file
with open("md_data.md", "w", encoding="utf-8") as f:
    f.write(md_data)
response = transform_chat_json(md_data)
response = re.sub(r"```json", '', response)
response = re.sub(r"```", '', response)


def upload_standard_data_to_mongodb(json_data, improved_user_id):
    uri = "mongodb+srv://leoyuruiqing:WziECEdgjZT08Xyj@airesume.niop3nd.mongodb.net/?retryWrites=true&w=majority&appName=AIResume"
    client = MongoClient(uri)

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    database_name = "airesumedb"
    collection_name = "improvedUsers"
    db = client[database_name]

    collection = db[collection_name]

    resume_id = "resume_2"

    collection.insert_one({"_id": improved_user_id, "personal_data": json.loads(json_data)})

    # 关闭MongoDB连接
    client.close()


upload_standard_data_to_mongodb(response, improved_user_id)
print(response)
