from openai import OpenAI




def kimi_generate(prompt):
    client = OpenAI(
        api_key="sk-XvJ2ykoX0G0i9J4Jxdcc6LILuWTvJTDHfqKlc8QZF9HU2u4x",
        base_url="https://api.moonshot.cn/v1",
    )

    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system",
             "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
    )
    return completion.choices[0].message.content



if __name__ == "__main__":
    prompt = "你好，今天的天气怎么样？"
    response = kimi_generate(prompt)
    print(response)