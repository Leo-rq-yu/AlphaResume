const express = require('express');
const cors = require('cors');
const app = express();
const path = require('path');
const jobInfoRoutes = require('./routes/jobInfoRoutes');
const resumeRoutes = require('./routes/resumeRoutes');
const chatHisRoutes = require('./routes/chatHisRoutes');
const impUserRoutes = require('./routes/impUserRoutes');
const resumeChatRoutes = require('./routes/resumeChatRoutes');
const authRoutes = require('./routes/authRoutes');
const resumeTemplateRoutes = require('./routes/resumeTemplateRoutes');
const resumeGuidanceRoutes = require('./routes/resumeGuidanceRoutes');
const resumeAudioRoutes = require('./routes/resumeAudioRoutes');
const interviewChatRoutes = require('./routes/interviewChatRoutes');
const hiringInfoRoutes = require('./routes/HiringInfoRoutes');
require('dotenv').config();

app.use(cors({
   origin: ['https://be.alpharesumeai.com', 'http://localhost:3000', 'https://www.alpharesumeai.com'], // 允许访问的前端地址
   methods: 'GET,POST,PUT,DELETE',
   allowedHeaders: 'Content-Type'
 }));

app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use('/api', jobInfoRoutes);
app.use('/api', resumeRoutes);
app.use('/api', chatHisRoutes);
app.use('/api', impUserRoutes);
app.use('/api', resumeChatRoutes);
app.use('/api', authRoutes);
app.use('/api',resumeTemplateRoutes);
app.use('/api', resumeGuidanceRoutes);
app.use('/api', resumeAudioRoutes);
app.use('/api', interviewChatRoutes);
app.use('/api', hiringInfoRoutes);
const { Queue, Worker } = require('bull');
const WebSocket = require('ws');
const http = require('http');
const { spawn } = require('child_process');
const fs = require('fs');

const { connect } = require('./mongodb/dbconfig');
const User = require('./mongodb/models/User');

let processResult = {};

app.get('/api/healthcheck', async (req, res) => {
   res.status(200).json("hello world");
});

// Route for handling POST requests
app.post('/api/resume', async (req, res) => {
   try {
      const db = await connect();
      const user = new User(req.body.id, req.body.基本信息, req.body.教育经历, req.body.工作_实习经历, req.body.项目经历, req.body.获奖信息, req.body.语言能力, req.body.技能);
      // console.log(req.body);
      const collection = db.collection('users');
      await collection.insertOne(user)
   } catch (err) {
      res.status(500).json({ message: 'Error storing data', error: err });
   }

   const pythonProcess = spawn('python3', ['./pyScripts/ResumeProcess.py', req.body.id]);
   processResult[req.body.id] = { status: 'running', path: "./outputResume/" + req.body.id + ".md" };
   console.log('Python process started');
   // console.log(processResult);

   pythonProcess.stdout.on('data', (data) => {
      console.log(`${data.toString("utf-8")}`);
   });

   pythonProcess.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
   });

   pythonProcess.on('close', (code) => {
      console.log(`child process exited with code ${code}`);
      processResult[req.body.id].status = 'done';
      // console.log(processResult);
   });

   res.status(200).json({ message: 'Data stored successfully', id: req.body.id });

});

app.get('/api/result/:id', (req, res) => {
   const id = req.params.id;
   console.log(id);
   const result = processResult[id];
   if (!result) {
      return res.status(404).json({ message: 'No result found' });
   }
   if (result.status === 'running') {
      return res.status(202).json({ message: 'Result is still running' });
   }
   if (result.status === 'done') {
      fs.readFile(result.path, 'utf-8', (err, data) => {
         if (err) {
            return res.status(500).json({ message: 'Error reading file', error: err });
         }
         return res.type('text/markdown').status(200).json({ result: data });
      });
   }
   // fs.readFile('./outputResume/sample.md', 'utf-8', (err, data) => {
   //    if (err) {
   //       return res.status(500).json({ message: 'Error reading file', error: err });
   //    }
   //    return res.type('text/markdown').status(200).json({result: data});
   // });
});

app.get('/api/file/:id', (req, res) => {
   const id = req.params.id;
   const result = processResult[id];
   fs.access(result.path, fs.F_OK, (err) => {
      if (err) {
         return res.status(404).json({ message: 'File not found' });
      }
      res.setHeader('Content-Type', 'application/pdf');
      const filestream = fs.createReadStream(result.path);
      filestream.pipe(res);
   });
});

// Define port
const port =  8080;
// Start the server
app.listen(port, () => {
   console.log(`Server listening at${port}`);
});
