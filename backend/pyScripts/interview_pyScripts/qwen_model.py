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

def generate_response(prompt):
    dashscope.api_key = 'sk-3c43423c9fee4af8928fd8bc647291ee'

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
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.


if __name__ == '__main__':
    prompt = "What is the meaning of life?"
    print(generate_response(prompt))