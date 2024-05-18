import sys
import io
import qwen
import re
import dashscope
from http import HTTPStatus
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# from dotenv import load_dotenv
import os
import time
import utlis as ut

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

dashscope.api_key='sk-3c43423c9fee4af8928fd8bc647291ee'

userId = sys.argv[1]

# get database
# load_dotenv()
mongodb_url = os.getenv('MONGODB_URL')
client = MongoClient(mongodb_url)
database_name = "airesumedb"
db = client[database_name]

# get original personal cv json
# userId = '662db8610d04dcf0a4ba0351'
cv_json = ut.get_cv_from_mongodb(db, userId)
print(cv_json)

# get job imformation
job_name = '软件工程师'
job_json = ut.get_job_info_from_mongodb(db, job_name)

information = {
    '用户信息': cv_json,
    '应聘岗位': job_name,
    '岗位信息': job_json
    }

job_keywords = information['岗位信息']["工作内容关键词"]
target_list = ["项目经历","技能","科研论文与知识产权"]
notarget_list = ['基本信息','教育经历',"获奖与证书","语言"]
keywords_target_list = ["职业经历"]
cv_key_order = ['基本信息','教育经历','职业经历','项目经历','科研论文与知识产权','技能','获奖与证书','语言']

# get improved personal cv json
improved_cv_json = ut.get_improved_cv_json(information, cv_key_order, notarget_list, target_list, keywords_target_list, job_keywords)
time.sleep(1)

# turn json cv into markdown
first_cv_json, second_cv_json = ut.split_cv_into_twoparts(improved_cv_json)
improved_cv_first_md = qwen.writeCV_first(first_cv_json)
time.sleep(1)
improved_cv_second_md = qwen.wirteCV_second(improved_cv_first_md, second_cv_json)
time.sleep(1)

improved_cv_first_md = re.sub(r'```markdown','',improved_cv_first_md)
improved_cv_first_md = re.sub(r'---\n\n','',improved_cv_first_md)
improved_cv_first_md = re.sub(r'```','',improved_cv_first_md)
improved_cv_second_md = re.sub(r'```markdown','',improved_cv_second_md)
improved_cv_second_md = re.sub(r'---\n\n','',improved_cv_second_md)
improved_cv_second_md = re.sub(r'```','',improved_cv_second_md)

improved_cv_md = improved_cv_first_md + '\n\n' +improved_cv_second_md

# get resume template
with open('./pyScripts/Resume_template.md', encoding='utf-8') as f:
    template = f.read()
with open('./pyScripts/Resume_template_null.md', encoding='utf-8') as f:
    template_null = f.read()

# get standard cv
md_simple = qwen.wirteCV_simple(template_null, template, improved_cv_md)

md_simple = re.sub(r'```markdown\n','',md_simple)
md_simple = re.sub(r'```','',md_simple)

# with open('Resume_API\simple_cv.md', 'w', encoding='utf-8') as f:
#     f.write(md_simple)

# results send back to database
# feedback_cv = {
#     "improved_cv_md" : md_simple,
#     "improved_cv_json": improved_cv_json,
#     "resumeId" : 'improved_resume_4',
#     "_id": '6621e0f77b5f95efede7b4fc'
# }

feedback_cv = {
    "improved_cv_md" : md_simple,
    "improved_cv_json": improved_cv_json,
    "resumeId" : 'improved_resume_4',
    "_id": userId
}

ut.send_cv_to_mongodb(db, feedback_cv)
print('generate and send resume successfully!')
