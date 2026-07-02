import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { spawn, exec } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

let mainWindow;
let trackerProcess = null;
let peerProcess = null;

function killProcessTree(proc) {
  if (!proc || !proc.pid) return;
  if (process.platform === 'win32') {
    exec(`taskkill /F /T /PID ${proc.pid}`, () => {});
  } else {
    try { proc.kill('SIGTERM'); } catch (e) {}
  }
}

function startBackend() {
  const isDev = !app.isPackaged || process.env.NODE_ENV === 'development';

  if (isDev) {
    // In Dev Mode: Run Python directly using virtual environment if available
    const trackerDir = path.join(__dirname, '../../backend/tracker');
    const peerDir = path.join(__dirname, '../../backend/peer');

    const winTrackerPython = path.join(trackerDir, '.venv/Scripts/python.exe');
    const winPeerPython = path.join(peerDir, '.venv/Scripts/python.exe');

    const trackerPython = fs.existsSync(winTrackerPython) ? winTrackerPython : 'python';
    const peerPython = fs.existsSync(winPeerPython) ? winPeerPython : 'python';

    console.log('[Electron] Starting Dev Tracker via:', trackerPython);
    trackerProcess = spawn(trackerPython, ['app/main.py'], { cwd: trackerDir, stdio: 'inherit', windowsHide: true });

    console.log('[Electron] Starting Dev Peer via:', peerPython);
    peerProcess = spawn(peerPython, ['app/main.py'], { cwd: peerDir, stdio: 'inherit', windowsHide: true });
  } else {
    // In Production Mode: Run compiled standalone PyInstaller binaries from resourcesPath
    const binDir = path.join(process.resourcesPath, 'binaries');
    const trackerExe = path.join(binDir, process.platform === 'win32' ? 'tracker.exe' : 'tracker');
    const peerExe = path.join(binDir, process.platform === 'win32' ? 'peer.exe' : 'peer');

    console.log('[Electron] Starting Prod Tracker binary:', trackerExe);
    trackerProcess = spawn(trackerExe, [], { stdio: 'ignore', windowsHide: true });

    console.log('[Electron] Starting Prod Peer binary:', peerExe);
    peerProcess = spawn(peerExe, [], { stdio: 'ignore', windowsHide: true });
  }

  trackerProcess?.on('error', (err) => console.error('[Electron] Tracker error:', err));
  peerProcess?.on('error', (err) => console.error('[Electron] Peer error:', err));
}

function killBackend() {
  console.log('[Electron] Terminating background Python processes...');
  if (trackerProcess) {
    killProcessTree(trackerProcess);
    trackerProcess = null;
  }
  if (peerProcess) {
    killProcessTree(peerProcess);
    peerProcess = null;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 960,
    minHeight: 600,
    title: 'MeshCDN Desktop',
    icon: fs.existsSync(path.join(__dirname, '../public/icon.ico'))
      ? path.join(__dirname, '../public/icon.ico')
      : path.join(__dirname, '../public/favicon.svg'),
    autoHideMenuBar: true,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });

  mainWindow.removeMenu();

  if (!app.isPackaged || process.env.NODE_ENV === 'development') {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

ipcMain.handle('dialog:openFile', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    title: 'Select File to Share with Swarm',
  });
  if (canceled) {
    return null;
  }
  return filePaths[0];
});

ipcMain.on('window:minimize', () => mainWindow?.minimize());
ipcMain.on('window:maximize', () => {
  if (mainWindow?.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow?.maximize();
  }
});
ipcMain.on('window:close', () => mainWindow?.close());

app.whenReady().then(() => {
  startBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('before-quit', () => {
  killBackend();
});

app.on('will-quit', () => {
  killBackend();
});

app.on('window-all-closed', () => {
  killBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
