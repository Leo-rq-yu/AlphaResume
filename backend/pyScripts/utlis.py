from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import qwen
import time

def get_cv_from_mongodb(db, user_id):  # user's id
    collection_name = "improvedUsers"
    collection = db[collection_name]
    query = {'_id': user_id}
    cv_cursor = collection.find(query)
    results = [doc for doc in cv_cursor]
    return results[0]['personal_data']

def get_job_info_from_mongodb(db, job_name): # job's id
    collection_name = "jobInformation"
    collection = db[collection_name]
    query = {'岗位名称': job_name}
    job_cursor = collection.find(query)
    results = [doc for doc in job_cursor]
    return results[0]

def get_improved_cv_json(information, cv_key_order, notarget_list, target_list, keywords_target_list, job_keywords):
    improved_cv_json = {}
    num = 9
    for key in cv_key_order:
        if key in notarget_list:
            improved_cv_json[key] = information['用户信息'][key]
        if key in target_list:
            improved_cv_json[key] = qwen.QA(key,information)
            time.sleep(1)
        if key in keywords_target_list:
            improved_cv_json[key] = qwen.QAKeywords(key,job_keywords,information)
            time.sleep(1)
        num += 5
        print(f'PROGRESS: {num}', flush=True)
    return improved_cv_json

def split_cv_into_twoparts(improved_cv_json):
    key_list = list(improved_cv_json.keys())
    first_cv_part = key_list[:4]
    second_cv_part = key_list[4:]
    first_cv_json = {}
    second_cv_json = {}
    for key, value in improved_cv_json.items():
        if key in first_cv_part:
            first_cv_json[key] = value
        elif key in second_cv_part:
            second_cv_json[key] = value
    return (first_cv_json, second_cv_json)

def send_cv_to_mongodb(db, insert_data):
    collection_name = "improvedUsers"
    collection = db[collection_name]
    record_id = insert_data.pop('_id', None)
    
    if record_id is None:
        return 'Error: No _id provided in update data.'
    # try:
    #     record_id = ObjectId(record_id)
    # except InvalidId:
    #     return 'Error: Invalid _id format.'

    result = collection.update_one({'_id': record_id}, {'$set': insert_data})
    
    if result.matched_count == 0:
        return 'No record found with the specified _id.'
    elif result.modified_count == 0:
        return 'No changes were made to the existing record.'
    else:
        return 'Update successfully!'
