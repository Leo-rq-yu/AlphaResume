const express = require('express');
const router = express.Router();
const { sendSms, generateVerificationCode } = require('../services/smsService');
const Account = require('../mongodb/models/Account');
const VerificationCode = require('../mongodb/models/VerificationCode');
const improvedUser = require('../mongodb/models/ImprovedUser');
const resumeHistory = require('../mongodb/models/ResumeHistory');
const { ObjectId } = require('mongodb');

// 假设你有一个用于发送验证码的路由
// authRoutes.js
router.post('/send-verification-code', async (req, res) => {
    const { phoneNumber } = req.body;
    const verificationCode = generateVerificationCode();
    const expiresAt = new Date(new Date().getTime() + 300000); // 5分钟后过期

    try {
        const codeRecord = new VerificationCode(phoneNumber, verificationCode, expiresAt);
        await codeRecord.save();
        const response = await sendSms(phoneNumber, '智芝全AI简历', 'SMS_465423748', JSON.stringify({ code: verificationCode }));
        res.status(200).json({ message: '验证码已发送', response });
    } catch (error) {
        res.status(500).json({ message: '发送验证码失败', error: error.toString() });
    }
});


// authRoutes.js - 修改登录逻辑，使其更加明确
router.post('/login', async (req, res) => {
    const { phoneNumber, code } = req.body;

    try {
        // Step 1: 验证码验证
        const validCode = await VerificationCode.findValidCode(phoneNumber, code);
        if (!validCode) {
            return res.status(401).json({ message: '验证码无效或已过期' });
        }

        // Step 2: 删除已验证的验证码
        await VerificationCode.deleteOne({ phoneNumber, code });

        // Step 3: 登录或创建新账户
        let account = await Account.findByPhoneNumber(phoneNumber);
        if (!account) {
            // 如果账户不存在，则创建一个新账户
            const newAccount = new Account({ phoneNumber, nickname: '新用户', avatar: '', improvedUsers: [] });
            const newAccountId = await newAccount.save();
            //account = await Account.findById(newAccountId);
            res.status(201).json({ message: '新账户已创建', phoneNumber: phoneNumber, id: newAccountId.toString() });
        } else {
            res.status(200).json({ message: '成功登录', phoneNumber: phoneNumber, id: account._id.toString() });
        }
    } catch (error) {
        console.error('登录或验证失败:', error);
        res.status(500).json({ message: '登录或验证失败', error: error.toString() });
    }
});

router.get('/account/:id', async (req, res) => {
    const { id } = req.params;
    try {
        const account = await Account.findById(id);
        if (!account) {
            return res.status(404).json({ message: '账户不存在' });
        }
        const resumeIdList = account.improvedUsers;
        res.status(200).json({ resumeIdList: resumeIdList });
    } catch (error) {
        console.error('获取账户失败:', error);
        res.status(500).json({ message: '获取账户失败', error: error.toString() });
    }
});

router.delete('/account/clear-history/:id', async (req, res) => {
    const { id } = req.params;
    console.log('id:', id);
    try {
        // const account = await Account.findById(id);
        // const improvedUsers = account.improvedUsers;
        // for (const improvedUserId of improvedUsers) {
        //     const resumeId = await improvedUser.getResumeId(improvedUserId);
        //     await resumeHistory.deleteById(resumeId);
        //     await improvedUser.deleteById(improvedUserId);
        // }
        const deleteResult = await Account.deleteAllImprovedUsers(id);
        if (deleteResult.modifiedCount === 0) {
            return res.status(404).json({ message: '未找到历史记录' });
        }
        res.status(200).json({ message: '已清空历史记录' });
    } catch (error) {
        console.error('清空历史记录失败:', error);
        res.status(500).json({ message: '清空历史记录失败', error: error.toString() });
    }
});


module.exports = router;