import { Capacitor } from '@capacitor/core';
import { Filesystem, Directory, Encoding } from '@capacitor/filesystem';

const isElectron = () => {
    return window.electronAPI && window.electronAPI.isElectron;
};

const isNative = () => {
    return Capacitor.isNativePlatform();
};

// Base path for external storage
const DB_PATH = 'EzeeGenie/db';

export const api = {
    /**
     * Helper to read JSON file from filesystem
     */
    async readJsonFile(path) {
        try {
            const contents = await Filesystem.readFile({
                path: `${DB_PATH}/${path}`,
                directory: Directory.Documents,
                encoding: Encoding.UTF8
            });
            return JSON.parse(contents.data);
        } catch (e) {
            console.error('Error reading file:', path, e);
            return null;
        }
    },

    /**
     * Get subjects data
     */
    async getSubjects() {
        if (isElectron()) {
            return await window.electronAPI.getSubjects();
        } else if (isNative()) {
            try {
                // 1. Read subject order
                const orderData = await this.readJsonFile('subject-order.json');
                const subjectOrderMap = {};
                if (orderData && orderData.subjectOrder) {
                    orderData.subjectOrder.forEach(item => {
                        subjectOrderMap[item.id.toLowerCase()] = item.order;
                        subjectOrderMap[item.displayName.toLowerCase().replace(/\s+/g, '-')] = item.order;
                        subjectOrderMap[item.displayName.toLowerCase()] = item.order;
                    });
                }

                // 2. Scan DB directory
                const result = await Filesystem.readdir({
                    path: DB_PATH,
                    directory: Directory.Documents
                });

                const subjectsList = [];

                // 3. Process each subdirectory
                for (const entry of result.files) {
                    if (entry.type === 'directory') {
                        const subjectData = await this.readJsonFile(`${entry.name}/subject.json`);
                        if (subjectData && subjectData.isActive) {
                            subjectsList.push(subjectData);
                        }
                    }
                }

                // 4. Aggregate (Simplified version of server logic)
                const publishersMap = {};

                subjectsList.forEach(subj => {
                    const pubName = subj.publisher || "Default Publisher";
                    const stdNum = subj.Standard;

                    if (!publishersMap[pubName]) {
                        publishersMap[pubName] = {
                            id: "pub_" + pubName.toLowerCase().replace(/\s+/g, ''),
                            publisherName: pubName,
                            standardsMap: {}
                        };
                    }

                    const pubObj = publishersMap[pubName];

                    if (!pubObj.standardsMap[stdNum]) {
                        pubObj.standardsMap[stdNum] = {
                            id: "std_" + stdNum,
                            standardName: String(stdNum),
                            standardInt: stdNum,
                            subjects: []
                        };
                    }

                    pubObj.standardsMap[stdNum].subjects.push({
                        id: subj.id,
                        subjectName: subj.subjectName,
                    });
                });

                // Convert Maps to Arrays and Sort
                const publishers = Object.values(publishersMap).map(pub => {
                    const standards = Object.values(pub.standardsMap).map(std => {
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
                    standards.sort((a, b) => a.standardInt - b.standardInt);
                    return { ...pub, standards };
                });

                return { publishers };

            } catch (e) {
                console.error('Error fetching subjects from filesystem:', e);
                // Return empty structure or throw
                throw new Error('Failed to load subjects from storage');
            }
        } else {
            const response = await fetch('/api/subjects');
            if (!response.ok) throw new Error('Failed to fetch subjects');
            return await response.json();
        }
    },

    /**
     * Get concept data for a specific standard/subject
     */
    async getConcept(standard, subject) {
        const subjectSlug = subject.toLowerCase().replace(/\s+/g, '-');

        if (isElectron()) {
            return await window.electronAPI.getConcept(standard, subjectSlug);
        } else if (isNative()) {
            const data = await this.readJsonFile(`${standard}-${subjectSlug}/concept.json`);
            if (!data) throw new Error('Concept data not found');
            return data;
        } else {
            const response = await fetch(`/api/concept/${standard}/${subjectSlug}`);
            if (!response.ok) throw new Error('Failed to fetch concept');
            return await response.json();
        }
    },

    /**
     * Get Q&A data for a specific standard/subject
     */
    async getQA(standard, subject) {
        const subjectSlug = subject.toLowerCase().replace(/\s+/g, '-');

        if (isElectron()) {
            return await window.electronAPI.getQA(standard, subjectSlug);
        } else if (isNative()) {
            const data = await this.readJsonFile(`${standard}-${subjectSlug}/qa.json`);
            if (!data) throw new Error('Q&A data not found');
            return data;
        } else {
            const response = await fetch(`/api/qa/${standard}/${subjectSlug}`);
            if (!response.ok) throw new Error('Failed to fetch Q&A');
            return await response.json();
        }
    },

    /**
     * Check if subject has valid data
     */
    async checkSubjectAvailability(standard, subject) {
        try {
            const data = await this.getConcept(standard, subject);
            return data && data.chapters && data.chapters.length > 0;
        } catch (e) {
            return false;
        }
    },

    /**
     * Resolve /db/ path to usable URL
     */
    async resolveDbPath(path) {
        if (!path || !path.startsWith('/db/')) return path;

        if (isNative()) {
            try {
                // path is like /db/10-science/images/foo.png
                // We need to strip /db/ to get EzeeGenie/db/10-science/images/foo.png
                // relative to Documents folder, DB_PATH is EzeeGenie/db

                const relativePath = path.substring(4); // Remove /db/
                const fullPath = `${DB_PATH}/${relativePath}`;

                const uri = await Filesystem.getUri({
                    path: fullPath,
                    directory: Directory.Documents
                });
                return Capacitor.convertFileSrc(uri.uri);
            } catch (e) {
                console.error("Error resolving DB path", path, e);
                return path; // Fallback
            }
        } else {
            return path;
        }
    }
};

export default api;
