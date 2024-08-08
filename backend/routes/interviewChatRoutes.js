const express = require('express');
const router = express.Router();
const InterviewChat = require('../mongodb/models/InterviewChat'); 
const { spawn } = require('child_process');
const path = require('path');

// 获取 Python 脚本的绝对路径
const initPythonScriptPath = path.resolve(__dirname, '../pyScripts/interview_pyScripts/question_initialization.py');
const version1PythonScriptPath = path.resolve(__dirname, '../pyScripts/interview_pyScripts/version1.py');

router.post('/interview-chat', async (req, res) => {
    try {
        const { userAccount, messages, resumeId, interviewTitle, companyName, position, interviewType } = req.body;

        // 首先创建 InterviewChat 对象并保存，获取 _id
        const interviewChat = new InterviewChat(userAccount, messages, resumeId, interviewTitle, companyName, position, interviewType);
        const _id = await interviewChat.save();

        // 然后运行 question_initialization.py 并传递 _id
        const initPythonProcess = spawn('python', [initPythonScriptPath, _id,resumeId]);

        let pythonOutput = '';

        initPythonProcess.stdout.on('data', (data) => {
            console.log(`Python Output: ${data.toString()}`);
            pythonOutput += data.toString();
        });

        initPythonProcess.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
        });

        initPythonProcess.on('close', (code) => {
            console.log(`question_initialization.py exited with code ${code}`);

            // 返回下一个问题给前端
            res.status(200).json({ id: _id, resumeId: resumeId, nextQuestion: pythonOutput.trim() });
        });

    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Failed to create interview chat', error: error.toString() });
    }
});

router.put('/interview-chat/:_id', async (req, res) => {
    try {
        const _id = req.params._id;
        const { quesId, answer, answer_type } = req.body;

        await InterviewChat.addAnswer(_id, quesId, answer, answer_type);

        // 每次提问时运行 version1.py 并传递 _id
        const version1PythonProcess = spawn('python', [version1PythonScriptPath, _id]);

        let pythonOutput = '';

        version1PythonProcess.stdout.on('data', (data) => {
            console.log(`Python Output: ${data.toString()}`);
            pythonOutput += data.toString();
        });

        version1PythonProcess.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
        });

        version1PythonProcess.on('close', (code) => {
            console.log(`version1.py exited with code ${code}`);
            res.status(200).json({ message: 'Answer added and script executed successfully', nextQuestion: pythonOutput.trim() });
        });

    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Failed to add answer.", error: error.toString() });
    }
});

router.get('/interview-chat/user-account/:userAccount', async (req, res) => {
    try {
        const userAccount = req.params.userAccount;
        const chats = await InterviewChat.findByUserAccount(userAccount);
        res.status(200).json(chats);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Failed to retrieve chats.", error: error.toString() });
    }
});

module.exports = router;
