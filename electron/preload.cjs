const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    // Get subjects data
    getSubjects: () => ipcRenderer.invoke('get-subjects'),

    // Get concept data for a specific standard/subject
    getConcept: (standard, subject) => ipcRenderer.invoke('get-concept', standard, subject),

    // Get Q&A data for a specific standard/subject
    getQA: (standard, subject) => ipcRenderer.invoke('get-qa', standard, subject),

    // Get absolute path for images
    getImagePath: (relativePath) => ipcRenderer.invoke('get-image-path', relativePath),

    // Check if running in Electron
    isElectron: true
});
