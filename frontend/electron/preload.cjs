const { contextBridge, ipcRenderer, webUtils } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Trigger native OS file picker and return the absolute path
  selectFile: () => ipcRenderer.invoke('dialog:openFile'),
  // Securely get absolute filesystem path for dropped File objects
  getPathForFile: (file) => {
    try {
      return webUtils ? webUtils.getPathForFile(file) : (file.path || file.name);
    } catch (e) {
      return file.path || file.name;
    }
  },
  // Custom frameless window controls
  minimizeWindow: () => ipcRenderer.send('window:minimize'),
  maximizeWindow: () => ipcRenderer.send('window:maximize'),
  closeWindow: () => ipcRenderer.send('window:close'),
});
