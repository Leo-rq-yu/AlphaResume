const express = require('express');
const router = express.Router();
const ResumeChat = require('../mongodb/models/ResumeChat'); // 根据你实际的models文件路径修改
const ImprovedUser = require('../mongodb/models/ImprovedUser.js');
const { spawn } = require('child_process');
const path = require('path');

function formatDateString() {
    // Ensure the input is a Date object
    const dateObj = new Date();
    if (isNaN(dateObj)) {
        throw new Error('Invalid date');
    }
    
    // Extract month and day
    const month = dateObj.getMonth() + 1; // Months are zero-based
    const day = dateObj.getDate();

    // Format the date string
    const formattedString = `${month}月${day}日聊天生成简历`;

    return formattedString;
}

// 获取 Python 脚本的绝对路径
const pythonScriptPath = path.resolve(__dirname, '../pyScripts/AI_asking_xinghuo_method2.py');

router.post('/resume-chat', async (req, res) => {
    try {
        const { userAccount, messages } = req.body;
        console.log(messages);
        // const currentDate = getFormattedDate();
        const resumeTitle = formatDateString();
        const personal_data = {
            "基本信息": {
                "title": resumeTitle,
                "姓": "",
                "名": "",
                "手机号码": "",
                "邮箱": "",
                "微信号": ""
            },
            "个人评价": "",
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
                    }
                ],
                "证书": [
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
                }
            ],
            "技能": [
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
                    }
                ],
                "知识产权": [
                    {
                        "专利名称": "",
                        "专利号": "",
                        "申请/授权时间": "",
                        "描述": ""
                    }
                ]
            }
        };

        const newUser = new ImprovedUser(personal_data, new Date(), new Date(), "", 0);

        const resume_id = await newUser.save(userAccount);

        const resumeChat = new ResumeChat(userAccount, messages, resume_id);
        const _id = await resumeChat.save();

        // 调用 Python 文件
        const pythonProcess = spawn('python', [pythonScriptPath, _id, resume_id, 0]);

        let stderrOutput = '';

        pythonProcess.stdout.on('data', (data) => {
            console.log(data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
            stderrOutput += data.toString();
        });

        pythonProcess.on('close', async (code) => {
            console.log(`child process exited with code ${code}`);

            if (stderrOutput.includes('UserWarning')) {
                // Ignore specific pydantic warnings
                console.warn(`Ignored warning: ${stderrOutput}`);
            } else if (stderrOutput) {
                // Handle other errors
                return res.status(500).json({ message: 'Failed to add message', error: stderrOutput });
            }

            const record = await ResumeChat.findById(_id);
            const messageList = record.messages;
            const lastRoundOfChat = messageList[messageList.length - 1];
            const lastMessage = lastRoundOfChat.question;
            const quesId = lastRoundOfChat.id;
            res.status(200).json({ id: _id, message: lastMessage, quesId: quesId, resumeId: resume_id});
        });

    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Failed to create resume chat', error: error.toString() });
    }
});

router.put('/resume-chat/:_id', async (req, res) => {
    try {
        const _id = req.params._id;
        const chatRecord = await ResumeChat.findById(_id);
        const resumeId = chatRecord.resumeId;
        const { quesId, answer, answer_type } = req.body; // Assume the new message is sent in the request body
        await ResumeChat.addAnswer(_id, quesId, answer, answer_type);

        const sectionId = chatRecord.sectionId;

        // 调用 Python 文件
        const pythonProcess = spawn('python', [pythonScriptPath, _id, resumeId, sectionId]);

        let stderrOutput = '';

        pythonProcess.stdout.on('data', (data) => {
            console.log(data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
            stderrOutput += data.toString();
        });

        pythonProcess.on('close', async (code) => {
            console.log(`child process exited with code ${code}`);

            if (stderrOutput.includes('UserWarning')) {
                // Ignore specific pydantic warnings
                console.warn(`Ignored warning: ${stderrOutput}`);
            } else if (stderrOutput) {
                // Handle other errors
                return res.status(500).json({ message: 'Failed to add message', error: stderrOutput });
            }

            const record = await ResumeChat.findById(_id);
            const messageList = record.messages;
            const lastRoundOfChat = messageList[messageList.length - 1];
            const lastMessage = lastRoundOfChat.question;
            const quesId = lastRoundOfChat.id;
            res.status(200).json({ id: _id, message: lastMessage, quesId: quesId });
        });

    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Failed to add message.", error: error.toString() });
    }
});

router.get('/resume-chat/user-account/:userAccount', async (req, res) => {
    try {
        const userAccount = req.params.userAccount;
        const chats = await ResumeChat.findByUserAccount(userAccount);
        res.status(200).json(chats);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Failed to retrieve chats.", error: error.toString() });
    }
});

router.get('/resume-chat/:_id', async (req, res) => {
    try {
        const _id = req.params._id;
        const chat = await ResumeChat.findById(_id);
        console.log(chat);
        if (chat) {
            res.status(200).json(chat);
        } else {
            res.status(404).json({ message: 'Chat not found' });
        }
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Failed to retrieve chat.", error: error.toString() });
    }
});

router.delete('/resume-chat/:_id', async (req, res) => {
    try {
        const _id = req.params._id;
        await ResumeChat.deleteById(_id);
        res.json({ message: 'Chat deleted successfully' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Failed to delete chat', error: error.toString() });
    }
});
// 新增的接口
router.get('/resume-chat/completeness/:_id', async (req, res) => {
    try {
        const _id = req.params._id;
        const chatRecord = await ResumeChat.findById(_id);
        if (!chatRecord) {
            return res.status(404).json({ message: 'Chat not found' });
        }
        const resumeId = chatRecord.resumeId;
        const completeness = await ImprovedUser.getCompletenessById(resumeId);
        res.status(200).json({ completeness: completeness });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Failed to retrieve completeness.', error: error.toString() });
    }
});
module.exports = router;
