import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const router = express.Router();

// Base path for db folder - go up from routes/ to server/ to app/
const DB_BASE_PATH = path.join(__dirname, '..', '..', 'db');

// Helper to read JSON files
const readJsonFile = (filePath) => {
    try {
        console.log(`Reading file: ${filePath}`);
        const data = fs.readFileSync(filePath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error(`Error reading file ${filePath}:`, error.message);
        return null;
    }
};

// DEBUG endpoint - list directory contents
router.get('/debug', (req, res) => {
    const result = {
        dirname: __dirname,
        dbBasePath: DB_BASE_PATH,
        dbExists: fs.existsSync(DB_BASE_PATH),
        dbContents: [],
        cwd: process.cwd()
    };

    try {
        if (result.dbExists) {
            result.dbContents = fs.readdirSync(DB_BASE_PATH);

            // List contents of each subdirectory 
            result.subfolders = {};
            for (const item of result.dbContents) {
                const itemPath = path.join(DB_BASE_PATH, item);
                if (fs.statSync(itemPath).isDirectory()) {
                    result.subfolders[item] = fs.readdirSync(itemPath);
                }
            }
        }
    } catch (err) {
        result.error = err.message;
    }

    res.json(result);
});

// GET /api/subjects - Returns subjects.json
router.get('/subjects', (req, res) => {
    const filePath = path.join(DB_BASE_PATH, 'subjects.json');
    const data = readJsonFile(filePath);

    if (data) {
        res.json(data);
    } else {
        res.status(404).json({ error: 'Subjects data not found' });
    }
});

// GET /api/concept/:standard/:subject - Returns concept.json for a subject
router.get('/concept/:standard/:subject', (req, res) => {
    const { standard, subject } = req.params;
    const filePath = path.join(DB_BASE_PATH, `${standard}-${subject}`, 'concept.json');
    const data = readJsonFile(filePath);

    if (data) {
        res.json(data);
    } else {
        res.status(404).json({ error: 'Concept data not found', path: filePath });
    }
});

// GET /api/qa/:standard/:subject - Returns qa.json for a subject
router.get('/qa/:standard/:subject', (req, res) => {
    const { standard, subject } = req.params;
    const filePath = path.join(DB_BASE_PATH, `${standard}-${subject}`, 'qa.json');
    const data = readJsonFile(filePath);

    if (data) {
        res.json(data);
    } else {
        res.status(404).json({ error: 'Q&A data not found', path: filePath });
    }
});

export default router;

