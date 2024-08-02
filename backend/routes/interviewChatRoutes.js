const express = require('express');
const router = express.Router();
const InterviewChat = require('../mongodb/models/InterviewChat'); // 根据你实际的models文件路径修改
const ImprovedUser = require('../mongodb/models/ImprovedUser.js');
const { spawn } = require('child_process');
const path = require('path');

// 获取 Python 脚本的绝对路径
const pythonScriptPath = path.resolve(__dirname, '../pyScripts/AI_asking_method1.py');

router.post('/interview-chat', async (req, res) => {
    try {
        const { userAccount, messages,resume_id } = req.body;
        //const newUser = new ImprovedUser(personal_data, new Date(), new Date(), "", 0);
        //const resume_id = await newUser.save(userAccount);
        const interviewChat = new InterviewChat(userAccount, messages, resume_id);
        const _id = await interviewChat.save();

        res.status(200).json({ id: _id, resumeId: resume_id });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Failed to create interview chat', error: error.toString() });
    }
});

router.put('/interview-chat/:_id', async (req, res) => {
    try {
        const _id = req.params._id;
        const { quesId, answer} = req.body; // Assume the new message is sent in the request body
        await InterviewChat.addAnswer(_id, quesId, answer);

        res.status(200).json({ message: 'Answer added successfully' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Failed to add answer.", error: error.toString() });
    }
});

router.delete('/interview-chat/:_id', async (req, res) => {
    try {
        const _id = req.params._id;
        await InterviewChat.deleteById(_id);
        res.json({ message: 'Chat deleted successfully' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Failed to delete chat', error: error.toString() });
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
