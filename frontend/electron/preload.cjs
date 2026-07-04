const { contextBridge, ipcRenderer, webUtils } = require('electron');

// Keep a map of dropped files to their absolute paths since contextBridge strips C++ file handles
const droppedFilePaths = new Map();

window.addEventListener('drop', (e) => {
  if (e.dataTransfer && e.dataTransfer.files) {
    for (const file of e.dataTransfer.files) {
      try {
        const path = webUtils ? webUtils.getPathForFile(file) : (file.path || file.name);
        if (path) {
          const key = `${file.name}-${file.size}-${file.lastModified}`;
          droppedFilePaths.set(key, path);
        }
      } catch (err) {
        console.error('Error extracting file path in preload:', err);
      }
    }
  }
}, true);

contextBridge.exposeInMainWorld('electronAPI', {
  // Trigger native OS file picker and return the absolute path
  selectFile: () => ipcRenderer.invoke('dialog:openFile'),
  // Securely get absolute filesystem path for dropped File objects
  getPathForFile: (file) => {
    try {
      if (!file) return null;
      const key = `${file.name}-${file.size}-${file.lastModified}`;
      if (droppedFilePaths.has(key)) {
        return droppedFilePaths.get(key);
      }
      return webUtils ? webUtils.getPathForFile(file) : (file.path || file.name);
    } catch {
      return file?.path || file?.name || null;
    }
  },
});

