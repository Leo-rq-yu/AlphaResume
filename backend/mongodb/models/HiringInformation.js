const { connect } = require('../dbconfig'); // 确保正确引入数据库配置
const { v4: uuidv4 } = require('uuid'); // 引入UUID库

class HiringInformation {
    constructor(data) {
        this._id = data._id || uuidv4(); // 生成UUID作为_id
        this.securityCode = data['证券代码'];
        this.originalCompanyName = data['原始公司名称'];
        this.relationshipWithListedCompany = data['与上市公司关系'];
        this.enterpriseType = data['企业类型'];
        this.marketValue = data['市值'];
        this.url = data['url'];
        this.companyName = data['公司名称'];
        this.associatedCompanyName = data['关联公司名称'];
        this.companyAddress = data['公司地址'];
        this.workLocationAreaCode = data['工作地点区域代码'];
        this.region = data['所在区域'];
        this.city = data['所在城市'];
        this.province = data['所在省份'];
        this.position = data['岗位'];
        this.positionDescription = data['岗位描述'];
        this.positionTags = data['岗位标签'];
        this.positionFunctions = data['岗位职能'];
        this.department = data['所属部门'];
        this.relatedBenefits = data['相关福利'];
        this.numberOfRecruits = data['招聘人数'];
        this.salary = data['待遇'];
        this.languageRequirements = data['语言要求'];
        this.yearsOfExperience = data['工作年限'];
        this.education = data['学历'];
        this.releaseTime = data['发布时间'];
    }

    // 保存新的岗位信息
    async save() {
        const db = await connect();
        const collection = db.collection('hiringInformation');
        const result = await collection.insertOne(this);
        return result.insertedId;
    }

    // 删除岗位信息
    static async deleteById(id) {
        const db = await connect();
        const collection = db.collection('hiringInformation');
        const result = await collection.deleteOne({ _id: id });
        return result;
    }

    // 根据条件查询岗位信息
    static async findByQuery(query) {
        const db = await connect();
        const collection = db.collection('hiringInformation');
        return await collection.find(query).toArray();
    }

    // 创建索引
    static async createIndexes() {
        const db = await connect();
        const collection = db.collection('hiringInformation');
        await collection.createIndex({ companyName: 1, position: 1, province: 1, city: 1 });
    }
}

module.exports = HiringInformation;
