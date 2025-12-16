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
        // console.log(`Reading file: ${filePath}`);
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
// GET /api/subjects - Returns aggregated subjects from folders
router.get('/subjects', (req, res) => {
    try {
        // 1. Read subject order
        const orderPath = path.join(DB_BASE_PATH, 'subject-order.json');
        const orderData = readJsonFile(orderPath);
        const subjectOrderMap = {};

        if (orderData && orderData.subjectOrder) {
            orderData.subjectOrder.forEach(item => {
                // Map both ID and Display Name (normalized) to order
                subjectOrderMap[item.id.toLowerCase()] = item.order;
                subjectOrderMap[item.displayName.toLowerCase().replace(/\s+/g, '-')] = item.order;
                subjectOrderMap[item.displayName.toLowerCase()] = item.order;
            });
        }

        // 2. Scan DB directory
        if (!fs.existsSync(DB_BASE_PATH)) {
            return res.status(500).json({ error: 'Database directory not found' });
        }

        const entries = fs.readdirSync(DB_BASE_PATH, { withFileTypes: true });
        const subjectsList = [];

        // 3. Process each subdirectory
        for (const entry of entries) {
            if (entry.isDirectory()) {
                const subjectJsonPath = path.join(DB_BASE_PATH, entry.name, 'subject.json');

                if (fs.existsSync(subjectJsonPath)) {
                    const subjectData = readJsonFile(subjectJsonPath);

                    // 4. Filter active subjects
                    if (subjectData && subjectData.isActive) {
                        subjectsList.push(subjectData);
                    }
                }
            }
        }

        // 5. Aggregate into response structure
        // Structure: parents -> publishers -> standards -> subjects
        // Since we only have one publisher (TNSB) implied in the old structure, we'll group by that.

        const publishersMap = {};

        subjectsList.forEach(subj => {
            const pubName = subj.publisher || "Default Publisher";
            const stdNum = subj.Standard; // Integer

            if (!publishersMap[pubName]) {
                publishersMap[pubName] = {
                    id: "pub_" + pubName.toLowerCase().replace(/\s+/g, ''), // Generate simple ID
                    publisherName: pubName,
                    standardsMap: {}
                };
            }

            const pubObj = publishersMap[pubName];

            if (!pubObj.standardsMap[stdNum]) {
                pubObj.standardsMap[stdNum] = {
                    id: "std_" + stdNum,
                    standardName: String(stdNum), // Frontend expects string
                    standardInt: stdNum, // For sorting
                    subjects: []
                };
            }

            pubObj.standardsMap[stdNum].subjects.push({
                id: subj.id,
                subjectName: subj.subjectName,
                // Add extra metadata if needed by frontend, but strictly sticking to existing structure for now
            });
        });

        // Convert Maps to Arrays and Sort
        const publishers = Object.values(publishersMap).map(pub => {
            const standards = Object.values(pub.standardsMap).map(std => {
                // Sort subjects
                std.subjects.sort((a, b) => {
                    const nameA = a.subjectName.toLowerCase();
                    const nameB = b.subjectName.toLowerCase();
                    const slugA = nameA.replace(/\s+/g, '-');
                    const slugB = nameB.replace(/\s+/g, '-');

                    const orderA = subjectOrderMap[slugA] || subjectOrderMap[nameA] || 999;
                    const orderB = subjectOrderMap[slugB] || subjectOrderMap[nameB] || 999;

                    return orderA - orderB;
                });
                return std;
            });

            // Sort standards numerically
            standards.sort((a, b) => a.standardInt - b.standardInt);

            return {
                id: pub.id,
                publisherName: pub.publisherName,
                standards: standards
            };
        });

        res.json({ publishers });

    } catch (error) {
        console.error("Error generating subjects list:", error);
        res.status(500).json({ error: 'Failed to generate subjects list' });
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

