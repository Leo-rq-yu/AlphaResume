from http import HTTPStatus
import dashscope
dashscope.api_key='sk-3c43423c9fee4af8928fd8bc647291ee'

# generate text
def QA(target,info_dict):
    requirements = f"根据我的信息库中所写的应聘岗位, 请先从我提供的信息库中的岗位信息了解该岗位所需的能力，然后按照你所了解到的岗位所需能力，对信息库中用户信息的{info_dict['用户信息'][target]}部分中的主观描述性语言进行详细地扩写，使我的经历介绍更加符合岗位所需，提升岗位匹配度。记住你只需要生成我指定的部分，不需要生成其它部分。所生成的文本要符合招聘要求，并能够体现岗位关键词。输出文本的格式与信息库中用户信息的{target}部分格式一致。"
    prompt = f"我想要应聘工作，需要你帮我生成一些文本用于制作简历，我将提供一个信息库,其中包含用户信息，应聘岗位及岗位信息。请你根据我提供的信息库，按照我提出的要求，生成相应的文本。请直接输出结果，不需要任何解释性语句与总结性语言。我的要求:{requirements},信息库:{info_dict}."

    response = dashscope.Generation.call(
        model='qwen-max-longcontext',
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
        print(response.usage)  
        return response.output['text']  
    else:
        print(response.code) 
        print(response.message) 


# generate text with keywords
def QAKeywords(target,keywords,info_dict):
    prompt = (
        f'你是一位专业的简历写手，我现在想让你帮我创作一些简历文本，我首先提供给你一个信息库，其中包含用户信息、应聘岗位以及岗位信息，请你首先了解这些信息。信息库：\n {info_dict}'
        f'另外我会提供给你我所应聘的这个工作内容关键词：{keywords}，这些关键词将帮助你更好地生成文本。'
        f"我希望你对信息库中的以下文本进行优化扩写: \n { info_dict['用户信息'][target] } \n"
        f'请你根据我所提供的工作流程关键词，并结合信息库中岗位信息的岗位关键词，对以上文本中的每段职业经历的 ''职责/业绩描述'' 文本按照工作流程关键词分为多段进行扩写，关键词放在扩写的每个小段的句首加粗表示。'
        f'你的扩写应使我的经历更能胜任该岗位的工作。输出文本的格式与信息库中用户信息的{target}部分格式一致，依然为多段职业经历，不要以关键词为分段依据。'
        f'请直接输出结果，不需要任何解释性语言与总结性语言。'
    )
    
    response = dashscope.Generation.call(
        model='qwen-max-longcontext',
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
        print(response.usage)  
        return response.output['text']  
    else:
        print(response.code)  
        print(response.message)


# convert json information to Markdown CV using Qwen
def writeCV_first(first_cv_json):
    prompt = f"我将提供一份JSON格式的简历信息，我希望能够生成一份Markdown格式的简历文本。请严格按照JSON中的文本来生成，不需要增加或删减任何文字。我的简历信息:{first_cv_json}"

    response = dashscope.Generation.call(
        model='qwen-max-longcontext',
        prompt= prompt,
        seed = 1234,
        top_p = 0.2,
        result_format = 'text',
        enable_search = False,
        max_tokens = 2000,
        temperature = 0.1,
        repetition_penalty = 1.0
    )

    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.

def wirteCV_second(improved_cv_first_md, second_cv_json):
    prompt = f"我想要完成一份Markdown格式的简历。我已经完成了一部分Markdown格式简历的撰写，如下：{improved_cv_first_md}。请根据我提供的JSON简历中的信息： {second_cv_json}， 完成剩余部分的Markdown简历的撰写。请注意格式及标题的统一，以便于我在之后将两部分Markdown简历拼接起来得到完整的简历。记住你只需要生成我提供的JSON格式的简历文本部分，不需要生成整个简历。"

    response = dashscope.Generation.call(
        model='qwen-max-longcontext',
        prompt= prompt,
        seed = 1234,
        top_p = 0.2,
        result_format = 'text',
        enable_search = False,
        max_tokens = 2000,
        temperature = 0.1,
        repetition_penalty = 1.0
    )

    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.

def wirteCV_simple(template_null, template, cv_md):
    prompt = (
        f"你是一位简历写作手，我希望你帮我创作一份中文简历。我会提供给你三份Markdown格式的简历，分别为：需要完善的Markdown简历1，已经完善的Markdown简历2，另外一份是Markdown格式的我的个人简历3。"
        f"待完善的简历1中需要填写的内容我已经为你进行了标识，我希望你将我的个人简历3中的文本经过适当精简后填入到简历1的对应位置。"
        f"你可以参考已经完善的简历2，我希望得到一份与之具有相同格式的简历，只是内容需要替换为我的个人简历中的信息。"
        f"你创作简历时需满足stev原则，突出保留简历中与职业相关的重点内容。"
        f"突出保留简历中与职业相关的重点内容，职业经历中的'职责/业绩描述'； 项目经历中的'项目描述'、'项目成就、'项目职责'；科研论文和知识产权中的'研究描述'。以上内容需要写得更丰富，尽量保留我所给的简历3中的信息。"
        f"需要完善的简历1: {template_null}."
        f"已经完善的简历2: {template}"
        f"个人简历: {cv_md}."
    )

    response = dashscope.Generation.call(
        model='qwen-max-longcontext',
        prompt= prompt,
        seed = 1234,
        top_p = 0.2,
        result_format = 'text',
        enable_search = False,
        max_tokens = 2000,
        temperature = 0.1,
        repetition_penalty = 1.0
    )

    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.


# convert json information to Markdown CV using Qwen
def writeCV(information, order):
    prompt = f"我将提供一份JSON格式的简历信息，请根据我提供的信息，按照{order}顺序帮我生成一份Markdown格式的简历模板。我的信息:{information}。"

    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_plus,
        prompt= prompt,
        seed = 1234,
        top_p = 0.2,
        result_format = 'text',
        enable_search = False,
        max_tokens = 2000,
        temperature = 0.1,
        repetition_penalty = 1.0
    )

    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.

# generate self-introduction based on improved cv and job
def write_self_introduction(cv,job):
    prompt = f"我想要应聘工作，请你根据我提供的个人简历(Markdown格式)以及所应聘的工作，帮助我生成一段自我介绍用于面试。个人简历:{cv}，应聘工作:{job}"

    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_plus,
        prompt= prompt,
        seed = 1234,
        top_p = 0.2,
        result_format = 'text',
        enable_search = False,
        max_tokens = 2000,
        temperature = 0.1,
        repetition_penalty = 1.0
    )

    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.

# generate questions based on improved cv
def write_interview_questions(cv,job,n):
    prompt = f"我想要应聘工作，假设你是面试官，请你根据我提供的个人简历(Markdown格式)以及所应聘的工作，生成你可能在面试中会提出的问题，数量为{n}个。个人简历:{cv}，应聘工作:{job}"

    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_plus,
        prompt= prompt,
        seed = 1234,
        top_p = 0.2,
        result_format = 'text',
        enable_search = False,
        max_tokens = 2000,
        temperature = 0.1,
        repetition_penalty = 1.0
    )

    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.

# generate questions' answers for reference based on cv and job
def write_questions_answers(questions,cv,job):
    prompt = f"我想要应聘工作，请你根据我提供的个人简历(Markdown格式)以及所应聘的工作，对我所提供的面试中可能遇到的问题进行回答。个人简历:{cv}，应聘工作:{job}，面试问题:{questions}"

    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_plus,
        prompt= prompt,
        seed = 1234,
        top_p = 0.2,
        result_format = 'text',
        enable_search = False,
        max_tokens = 2000,
        temperature = 0.1,
        repetition_penalty = 1.0
    )

    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.

# generate interview evaluation report
def write_interview_report(job,cv,interview_data,scoring_criteria):
    prompt = f"""假设你是一位面试官，刚刚面试了一位求职者，其应聘的岗位为{job}，应聘者的简历为{cv}，面试数据保存在{interview_data}中，包含求职者的自我介绍与面试问答内容。你现在需要对应聘者的面试表现进行评价，你有两份评价指标体系，总分均为100分，一分为普通评价指标体系{scoring_criteria['general']},用于对应聘者的面试一般能力进行评价；一份为专业评价指标体系{scoring_criteria['professional']}，用于对应聘者的专业能力进行评价。请你按照这两份评价指标体系，对应聘者的面试表现进行评估，完成一份评估报告。你的评估报告应包含面试者在两份评价指标体系中每个指标上的得分以及简要评价，然后你需要计算应聘者在两份评价指标体系上的总得分，最后你需要对应聘者进行一个综合的评价，并给出是否录取的建议。评估报告以JSON格式给出。"""

    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_plus,
        prompt= prompt,
        seed = 1234,
        top_p = 0.2,
        result_format = 'text',
        enable_search = False,
        max_tokens = 2000,
        temperature = 0.1,
        repetition_penalty = 1.0
    )

    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.


# generate evaluation for questions' answers in cv interview
def write_cv_qa_report(job,cv,scoring_criteria,question,answer):
    prompt = f"""假设你是一位面试官，刚刚面试了我，我应聘的岗位为{job}，我的简历为{cv}。你对我提出的问题为{question}，我的回答为{answer}。现在你需要对我的回答进行评价，根据评价准则{scoring_criteria}，结合我的简历以及你对应聘职位的理解，生成一段评价文本，你的评价应该以第二人称生成，包含我的回答的总体评价、优缺点，以及值得改进的地方。"""

    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_plus,
        prompt= prompt,
        seed = 1234,
        top_p = 0.2,
        result_format = 'text',
        enable_search = False,
        max_tokens = 2000,
        temperature = 0.1,
        repetition_penalty = 1.0
    )

    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.

# generate evaluation for questions' answers in tech interview
def write_tech_qa_report(job,question,answer):
    prompt = f"""假设你是一位面试官，刚刚面试了我，我应聘的岗位为{job}。你对我提出的问题为{question}，我的回答为{answer}。现在你需要对我的回答进行评价，结合你对应聘职位的理解，生成一段评价文本，你的评价应该以第二人称生成，包含我的回答的总体评价、正确性、完整性，以及值得改进的地方。"""

    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_plus,
        prompt= prompt,
        seed = 1234,
        top_p = 0.2,
        result_format = 'text',
        enable_search = False,
        max_tokens = 2000,
        temperature = 0.1,
        repetition_penalty = 1.0
    )

    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.

# generate evaluation for self introduction in interview
def write_self_introduction_report(job,cv,scoring_criteria,answer):

    prompt = f"""假设你是一位面试官，刚刚面试了我，我应聘的岗位为{job}，我的简历为{cv}。我的自我介绍为{answer}。现在你需要对我的自我介绍进行评价，根据评价准则{scoring_criteria}，结合我的简历以及你对应聘职位的理解，生成一段评价文本，你的评价应该以第二人称生成，包含我的自我介绍的总体评价、优缺点，以及值得改进的地方。"""

    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_plus,
        prompt= prompt,
        seed = 1234,
        top_p = 0.2,
        result_format = 'text',
        enable_search = False,
        max_tokens = 2000,
        temperature = 0.1,
        repetition_penalty = 1.0
    )

    if response.status_code == HTTPStatus.OK:
        print(response.usage)  # The usage information
        return response.output['text']  # The output text
    else:
        print(response.code)  # The error code.
        print(response.message)  # The error message.
