/**
 * API wrapper that works in both web and Electron environments.
 * In Electron, uses IPC calls. In web, uses fetch API.
 */

const isElectron = () => {
    return window.electronAPI && window.electronAPI.isElectron;
};

export const api = {
    /**
     * Get subjects data
     */
    async getSubjects() {
        if (isElectron()) {
            return await window.electronAPI.getSubjects();
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
    }
};

export default api;
