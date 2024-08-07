const express = require('express');
const router = express.Router();
const HiringInformation = require('../mongodb/models/HiringInformation'); // 确保路径与你的项目结构相匹配
const { connect } = require('../mongodb/dbconfig'); // 确保正确引入数据库配置

// 创建索引
HiringInformation.createIndexes().then(() => {
    console.log('Indexes created');
}).catch((err) => {
    console.error('Error creating indexes:', err);
});

// 添加岗位信息
router.post('/hiring', async (req, res) => {
    try {
        const hiringInfo = new HiringInformation(req.body);
        const insertedId = await hiringInfo.save();
        res.status(201).json({ message: 'Hiring information created successfully', _id: insertedId });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Failed to create hiring information', error: error.toString() });
    }
});

// 删除岗位信息
router.delete('/hiring/:id', async (req, res) => {
    try {
        const { id } = req.params;
        const result = await HiringInformation.deleteById(id);
        if (result.deletedCount === 0) {
            return res.status(404).json({ message: 'Hiring information not found' });
        }
        res.status(200).json({ message: 'Hiring information deleted successfully' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Failed to delete hiring information', error: error.toString() });
    }
});

// 删除集合中所有数据
router.delete('/hiringAll', async (req, res) => {
    try {
        const db = await connect();
        const collection = db.collection('hiringInformation');
        const result = await collection.deleteMany({});
        res.status(200).json({ message: 'All hiring information deleted successfully', deletedCount: result.deletedCount });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Failed to delete all hiring information', error: error.toString() });
    }
});

// 根据公司名、岗位、省份和城市查询
// 根据公司名、岗位、省份和城市查询
router.get('/hiring', async (req, res) => {
    try {
        const { companyName, position, province, city } = req.body;
        console.log(req.query);
        
        let query = {};
        let results = [];

        if (companyName) {
            query.companyName = companyName;
            results = await HiringInformation.findByQuery(query);
            if (results.length === 0) return res.status(200).json(results);
        }

        if (position) {
            query.position = position;
            results = results.filter(item => item.position === position);
            if (results.length === 0) return res.status(200).json(await HiringInformation.findByQuery({ companyName }));
        }

        if (province) {
            query.province = province;
            results = results.filter(item => item.province === province);
            if (results.length === 0) return res.status(200).json(await HiringInformation.findByQuery({ companyName, position }));
        }

        if (city) {
            query.city = city;
            results = results.filter(item => item.city === city);
            if (results.length === 0) return res.status(200).json(await HiringInformation.findByQuery({ companyName, position, province }));
        }

        res.status(200).json(results);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Failed to retrieve hiring information', error: error.toString() });
    }
});


module.exports = router;
