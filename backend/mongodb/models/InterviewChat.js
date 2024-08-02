const { connect } = require('../dbconfig');
const { v4: uuidv4 } = require('uuid'); // 引入UUID生成器

class InterviewChat {
    constructor(userAccount, messages, resumeId, id = null) {
        this._id = id || uuidv4(); // 使用 uuid 生成唯一标识符
        this.userAccount = userAccount;
        this.messages = messages; // 假设 messages 为一问一答数组
        this.resumeId = resumeId
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

    // static async addQuestion(_id, newQuestion) {
    //     const db = await connect();
    //     const collection = db.collection('interviewChats');
    //     return await collection.updateOne(
    //         { _id },
    //         { $push: { messages: { question: newQuestion, answer: "" } } }
    //     );
    // }

    static async addAnswer(_id, messageId, newAnswer, answer_type) {
        const db = await connect();
        const collection = db.collection('interviewChats');
        const document = await collection.findOne({ _id });
        console.log("Add answer")
        console.log(messageId)
        console.log(newAnswer)
        console.log(answer_type)
        console.log(document.messages)
        const messageIndex = document.messages.findIndex(message => message.id === messageId);
        console.log(messageIndex)

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
