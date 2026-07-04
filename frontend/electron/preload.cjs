const { contextBridge, ipcRenderer, webUtils } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Trigger native OS file picker and return the absolute path
  selectFile: () => ipcRenderer.invoke('dialog:openFile'),
  // Securely get absolute filesystem path for dropped File objects
  getPathForFile: (file) => {
    try {
      return webUtils ? webUtils.getPathForFile(file) : (file.path || file.name);
    } catch {
      return file.path || file.name;
    }
  },
});

