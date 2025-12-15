const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

// Determine if we're in development or production
const isDev = !app.isPackaged;

// Path to the db folder
const getDbPath = () => {
    if (isDev) {
        return path.join(__dirname, '..', 'db');
    } else {
        // In production, db is in resources folder
        return path.join(process.resourcesPath, 'db');
    }
};

// Helper to read JSON files
const readJsonFile = (filePath) => {
    try {
        const data = fs.readFileSync(filePath, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error(`Error reading file ${filePath}:`, error.message);
        return null;
    }
};

// IPC Handlers
ipcMain.handle('get-subjects', async () => {
    const filePath = path.join(getDbPath(), 'subjects.json');
    return readJsonFile(filePath);
});

ipcMain.handle('get-concept', async (event, standard, subject) => {
    const filePath = path.join(getDbPath(), `${standard}-${subject}`, 'concept.json');
    return readJsonFile(filePath);
});

ipcMain.handle('get-qa', async (event, standard, subject) => {
    const filePath = path.join(getDbPath(), `${standard}-${subject}`, 'qa.json');
    return readJsonFile(filePath);
});

ipcMain.handle('get-image-path', async (event, relativePath) => {
    // Convert relative path to absolute path for images
    const fullPath = path.join(getDbPath(), relativePath.replace('/db/', ''));
    if (fs.existsSync(fullPath)) {
        return `file://${fullPath}`;
    }
    return null;
});

let mainWindow;

const createWindow = () => {
    const iconPath = isDev
        ? path.join(__dirname, '..', 'public', 'icon.png')
        : path.join(app.getAppPath(), 'dist', 'icon.png');

    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        autoHideMenuBar: true,
        webPreferences: {
            preload: path.join(__dirname, 'preload.cjs'),
            contextIsolation: true,
            nodeIntegration: false
        },
        icon: iconPath
    });

    // Maximize window on startup
    mainWindow.maximize();

    // Enable DevTools shortcut (Ctrl+Shift+I) in production
    mainWindow.webContents.on('before-input-event', (event, input) => {
        if (input.control && input.shift && input.key.toLowerCase() === 'i') {
            mainWindow.webContents.toggleDevTools();
        }
    });

    if (isDev) {
        // Development: load from Vite dev server
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        // Production: load built files from app.asar
        const indexPath = path.join(app.getAppPath(), 'dist', 'index.html');
        console.log('Loading index.html from:', indexPath);
        console.log('App path:', app.getAppPath());
        console.log('DB path:', getDbPath());

        mainWindow.loadFile(indexPath).catch(err => {
            console.error('Failed to load index.html:', err);
        });
    }
};

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
