const { connect } = require('../dbconfig');
const { v4: uuidv4 } = require('uuid'); // 引入UUID生成器

class InterviewChat {
    constructor(userAccount, messages, resumeId, interviewTitle, companyName, position, interviewType, id = null) {
        this._id = id || uuidv4(); // 使用 uuid 生成唯一标识符
        this.userAccount = userAccount;
        this.messages = messages; // 假设 messages 为一问一答数组
        this.resumeId = resumeId;
        this.interviewTitle = interviewTitle;  // 新加的字段
        this.companyName = companyName;        // 新加的字段
        this.position = position;              // 新加的字段
        this.interviewType = interviewType;    // 新加的字段
        this.sectionId = 0;
    }

    async save() {
        const db = await connect();
        const collection = db.collection('interviewChats');
        const result = await collection.insertOne(this);
        return result.insertedId;
    }

    static async addMessage(_id, newMessage) {
        const db = await connect();
        const collection = db.collection('interviewChats');
        return await collection.updateOne(
            { _id },
            { $push: { messages: newMessage } }
        );
    }

    static async addAnswer(_id, messageId, newAnswer, answer_type) {
        const db = await connect();
        const collection = db.collection('interviewChats');
        const document = await collection.findOne({ _id });
    
        const messageIndex = document.messages.findIndex(message => message.id === messageId);
    
        if (messageIndex === -1) {
            const newItem = {
                id: messageId,
                question: "default question",
                answer: newAnswer,
                answer_type: answer_type
            };
    
            const updateResult = await collection.updateOne(
                { _id },
                { $push: { messages: newItem } }
            );
    
            return updateResult;
        } else {
            const updateFields = {
                [`messages.${messageIndex}.answer`]: newAnswer,
                [`messages.${messageIndex}.answer_type`]: answer_type
            };
    
            const updateResult = await collection.updateOne(
                { _id },
                { $set: updateFields }
            );
    
            return updateResult;
        }
    }

    static async findByUserAccount(userAccount) {
        const db = await connect();
        const collection = db.collection('interviewChats');
        return await collection.find({ userAccount }).toArray();
    }

    static async findById(_id) {
        const db = await connect();
        const collection = db.collection('interviewChats');
        return await collection.findOne({ _id });
    }

    static async deleteById(_id) {
        const db = await connect();
        const collection = db.collection('interviewChats');
        return await collection.deleteOne({ _id });
    }
}

module.exports = InterviewChat;
