import { createContext, useContext, useReducer, useCallback, useRef, useEffect } from 'react';
import { api } from '../services/api';

// ─── LocalStorage Helper ─────────────────────────
const loadSavedSettings = () => {
  try {
    const saved = localStorage.getItem('meshcdn_settings');
    if (saved) return JSON.parse(saved);
  } catch (e) {}
  return {};
};

// ─── Initial State ───────────────────────────────
const initialState = {
  // Connection Status
  trackerOnline: false,
  peerOnline: false,

  // Data
  files: [],
  peers: [],
  downloads: [],
  sharedFiles: [],
  activities: [],
  notifications: [],

  // Stats
  stats: {
    totalUploaded: 0,
    totalDownloaded: 0,
    filesShared: 0,
    filesDownloaded: 0,
    chunksUploaded: 0,
    chunksDownloaded: 0,
    storageUsed: 0,
  },

  // Speed tracking
  downloadSpeed: 0,
  uploadSpeed: 0,
  speedHistory: [],

  // Settings
  settings: {
    trackerUrl: 'http://localhost:8000',
    peerPort: 5000,
    downloadFolder: './downloads',
    uploadFolder: './uploads',
    maxUploadSpeed: 0,
    maxDownloadSpeed: 0,
    chunkSize: 1048576,
    autoStart: true,
    darkMode: false,
    developerMode: false,
    askBeforeDownload: true,
    ...loadSavedSettings(),
  },

  // UI State
  searchQuery: '',
  selectedFile: null,
  selectedPeer: null,
};

// ─── Actions ─────────────────────────────────────
const ActionTypes = {
  SET_TRACKER_STATUS: 'SET_TRACKER_STATUS',
  SET_PEER_STATUS: 'SET_PEER_STATUS',
  SET_FILES: 'SET_FILES',
  SET_PEERS: 'SET_PEERS',
  ADD_DOWNLOAD: 'ADD_DOWNLOAD',
  UPDATE_DOWNLOAD: 'UPDATE_DOWNLOAD',
  REMOVE_DOWNLOAD: 'REMOVE_DOWNLOAD',
  SET_SHARED_FILES: 'SET_SHARED_FILES',
  ADD_ACTIVITY: 'ADD_ACTIVITY',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  UPDATE_STATS: 'UPDATE_STATS',
  UPDATE_SPEED: 'UPDATE_SPEED',
  UPDATE_SETTINGS: 'UPDATE_SETTINGS',
  SET_SEARCH_QUERY: 'SET_SEARCH_QUERY',
  SET_SELECTED_FILE: 'SET_SELECTED_FILE',
  SET_SELECTED_PEER: 'SET_SELECTED_PEER',
};

// ─── Reducer ─────────────────────────────────────
function appReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_TRACKER_STATUS:
      return { ...state, trackerOnline: action.payload };

    case ActionTypes.SET_PEER_STATUS:
      return { ...state, peerOnline: action.payload };

    case ActionTypes.SET_FILES:
      return { ...state, files: action.payload };

    case ActionTypes.SET_PEERS:
      return { ...state, peers: action.payload };

    case ActionTypes.ADD_DOWNLOAD:
      return { ...state, downloads: [...state.downloads, action.payload] };

    case ActionTypes.UPDATE_DOWNLOAD:
      return {
        ...state,
        downloads: state.downloads.map((d) =>
          d.id === action.payload.id ? { ...d, ...action.payload } : d
        ),
      };

    case ActionTypes.REMOVE_DOWNLOAD:
      return {
        ...state,
        downloads: state.downloads.filter((d) => d.id !== action.payload),
      };

    case ActionTypes.SET_SHARED_FILES:
      return { ...state, sharedFiles: action.payload };

    case ActionTypes.ADD_ACTIVITY:
      return {
        ...state,
        activities: [action.payload, ...state.activities].slice(0, 50),
      };

    case ActionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        notifications: [...state.notifications, action.payload],
      };

    case ActionTypes.REMOVE_NOTIFICATION:
      return {
        ...state,
        notifications: state.notifications.filter((n) => n.id !== action.payload),
      };

    case ActionTypes.UPDATE_STATS:
      return { ...state, stats: { ...state.stats, ...action.payload } };

    case ActionTypes.UPDATE_SPEED:
      return {
        ...state,
        downloadSpeed: action.payload.downloadSpeed ?? state.downloadSpeed,
        uploadSpeed: action.payload.uploadSpeed ?? state.uploadSpeed,
        speedHistory: [
          ...state.speedHistory,
          {
            time: Date.now(),
            download: action.payload.downloadSpeed ?? state.downloadSpeed,
            upload: action.payload.uploadSpeed ?? state.uploadSpeed,
          },
        ].slice(-60),
      };

    case ActionTypes.UPDATE_SETTINGS:
      return { ...state, settings: { ...state.settings, ...action.payload } };

    case ActionTypes.SET_SEARCH_QUERY:
      return { ...state, searchQuery: action.payload };

    case ActionTypes.SET_SELECTED_FILE:
      return { ...state, selectedFile: action.payload };

    case ActionTypes.SET_SELECTED_PEER:
      return { ...state, selectedPeer: action.payload };

    default:
      return state;
  }
}

// ─── Context ─────────────────────────────────────
const AppContext = createContext(null);

// ─── Provider ────────────────────────────────────
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);
  const notifIdRef = useRef(0);
  const stateRef = useRef(state);

  useEffect(() => {
    stateRef.current = state;
    try {
      localStorage.setItem('meshcdn_settings', JSON.stringify(state.settings));
    } catch (e) {}
  }, [state]);

  // Notification helpers
  const addNotification = useCallback((type, title, message) => {
    const id = ++notifIdRef.current;
    dispatch({
      type: ActionTypes.ADD_NOTIFICATION,
      payload: { id, type, title, message, createdAt: Date.now() },
    });
    // Auto-remove after 5s
    setTimeout(() => {
      dispatch({ type: ActionTypes.REMOVE_NOTIFICATION, payload: id });
    }, 5000);
  }, []);

  const removeNotification = useCallback((id) => {
    dispatch({ type: ActionTypes.REMOVE_NOTIFICATION, payload: id });
  }, []);

  const addActivity = useCallback((type, message) => {
    dispatch({
      type: ActionTypes.ADD_ACTIVITY,
      payload: { id: Date.now(), type, message, timestamp: new Date().toISOString() },
    });
  }, []);

  // Data fetching
  const refreshStatus = useCallback(async () => {
    const [tracker, peer] = await Promise.all([
      api.getTrackerStatus(),
      api.getPeerStatus(),
    ]);
    dispatch({ type: ActionTypes.SET_TRACKER_STATUS, payload: tracker.online });
    dispatch({ type: ActionTypes.SET_PEER_STATUS, payload: peer.online });
  }, []);

  const refreshFiles = useCallback(async () => {
    try {
      const files = await api.getFiles();
      dispatch({ type: ActionTypes.SET_FILES, payload: files });
    } catch {
      // silently fail if tracker is offline
    }
  }, []);

  const refreshPeers = useCallback(async () => {
    try {
      const peers = await api.getPeers();
      dispatch({ type: ActionTypes.SET_PEERS, payload: peers });
    } catch {
      // silently fail
    }
  }, []);

  const refreshAll = useCallback(async () => {
    await Promise.all([refreshStatus(), refreshFiles(), refreshPeers()]);
  }, [refreshStatus, refreshFiles, refreshPeers]);

  // Actions
  const shareFile = useCallback(async (filePath) => {
    try {
      const result = await api.shareFile(filePath);
      addNotification('success', 'File Shared', `Successfully shared file`);
      addActivity('success', `Shared file`);
      await refreshFiles();
      return result;
    } catch (err) {
      addNotification('error', 'Share Failed', err.message);
      throw err;
    }
  }, [addNotification, addActivity, refreshFiles]);

  const downloadFile = useCallback(async (fileHash) => {
    let interval;
    const id = Date.now();
    try {
      let currentProgress = 0;
      
      dispatch({
        type: ActionTypes.ADD_DOWNLOAD,
        payload: {
          id,
          fileHash,
          progress: 0,
          speed: 0,
          peers: 0,
          eta: 'Calculating...',
          status: 'connecting',
          startedAt: Date.now(),
        },
      });
      addActivity('info', `Download started`);

      // Poll real progress from the backend while waiting for the blocking backend API
      interval = setInterval(async () => {
        const progressRes = await api.getDownloadProgress(fileHash);
        if (progressRes && progressRes.data) {
          const realProgress = progressRes.data.progress || 0;
          const realSpeed = progressRes.data.speed || 0;
          const realPeers = progressRes.data.peers || 1;
          const backendStatus = progressRes.data.status || 'downloading';
          
          let etaLabel = 'Downloading...';
          if (backendStatus === 'reconstructing') {
             etaLabel = 'Reconstructing file...';
          }
          
          dispatch({
            type: ActionTypes.UPDATE_DOWNLOAD,
            payload: { 
              id, 
              progress: Math.round(realProgress), 
              status: 'downloading',
              speed: realSpeed,
              peers: realPeers,
              eta: etaLabel
            },
          });
        }
      }, 500);

      const result = await api.downloadFile(fileHash);
      
      clearInterval(interval);
      dispatch({
        type: ActionTypes.UPDATE_DOWNLOAD,
        payload: { id, progress: 100, status: 'completed', eta: 'Done', speed: 0 },
      });
      
      // Ask user where to save the file based on setting
      if (result && result.data && result.data.file_name) {
        try {
          const ask = stateRef.current.settings.askBeforeDownload ?? true;
          if (ask && 'showSaveFilePicker' in window) {
            const handle = await window.showSaveFilePicker({
              suggestedName: result.data.file_name
            });
            const writable = await handle.createWritable();
            const response = await fetch(`http://localhost:5001/download/serve?file_name=${encodeURIComponent(result.data.file_name)}`);
            await response.body.pipeTo(writable);
          } else {
            // Save directly without asking or fallback for older browsers
            const response = await fetch(`http://localhost:5001/download/serve?file_name=${encodeURIComponent(result.data.file_name)}`);
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = result.data.file_name;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
          }
        } catch (e) {
          console.log('User cancelled save or save failed', e);
        }
      }
      
      addNotification('success', 'Download Complete', `File downloaded successfully`);
      addActivity('success', `Download completed`);
      await refreshFiles();
      return result;
    } catch (err) {
      if (interval) clearInterval(interval);
      if (err.message.toLowerCase().includes('cancel')) {
        dispatch({
          type: ActionTypes.UPDATE_DOWNLOAD,
          payload: { id, status: 'cancelled', eta: 'Cancelled', speed: 0 },
        });
        addNotification('warning', 'Download Cancelled', 'The download was cancelled.');
      } else {
        dispatch({
          type: ActionTypes.UPDATE_DOWNLOAD,
          payload: { id, status: 'failed', eta: 'Failed', speed: 0 },
        });
        addNotification('error', 'Download Failed', err.message);
      }
      throw err;
    }
  }, [addNotification, addActivity, refreshFiles]);

  const pauseDownload = useCallback(async (id, fileHash) => {
    try {
      await api.pauseDownload(fileHash);
      dispatch({ type: ActionTypes.UPDATE_DOWNLOAD, payload: { id, status: 'paused', speed: 0, eta: 'Paused' } });
      addNotification('info', 'Download Paused', 'Download has been paused');
    } catch (err) {
      console.error(err);
    }
  }, [addNotification]);

  const resumeDownload = useCallback(async (id, fileHash) => {
    try {
      await api.resumeDownload(fileHash);
      dispatch({ type: ActionTypes.UPDATE_DOWNLOAD, payload: { id, status: 'downloading', eta: 'Resuming...' } });
      addNotification('success', 'Download Resumed', 'Download has resumed');
    } catch (err) {
      console.error(err);
    }
  }, [addNotification]);

  const cancelDownload = useCallback(async (id, fileHash) => {
    try {
      await api.cancelDownload(fileHash);
      // State is updated by the catch block of downloadFile when the backend aborts
    } catch (err) {
      console.error(err);
    }
  }, []);

  const stopSharing = useCallback(async (fileHash) => {
    try {
      await api.stopSharing(fileHash);
      addNotification('success', 'Stopped Sharing', 'File is no longer shared');
      addActivity('info', 'Stopped sharing file');
      await refreshFiles();
    } catch (err) {
      addNotification('error', 'Error', err.message);
    }
  }, [addNotification, addActivity, refreshFiles]);

  const deleteFileAction = useCallback(async (fileHash) => {
    try {
      await api.deleteFile(fileHash);
      addNotification('success', 'File Deleted', 'File removed from network');
      addActivity('info', 'Deleted file');
      await refreshFiles();
    } catch (err) {
      addNotification('error', 'Error', err.message);
    }
  }, [addNotification, addActivity, refreshFiles]);

  const updateSettings = useCallback((newSettings) => {
    dispatch({ type: ActionTypes.UPDATE_SETTINGS, payload: newSettings });
  }, []);

  // Periodic refresh
  useEffect(() => {
    refreshAll();
    const interval = setInterval(refreshAll, 10000);
    return () => clearInterval(interval);
  }, [refreshAll]);

  const value = {
    state,
    dispatch,
    ActionTypes,
    // Actions
    addNotification,
    removeNotification,
    addActivity,
    refreshStatus,
    refreshFiles,
    refreshPeers,
    refreshAll,
    shareFile,
    downloadFile,
    pauseDownload,
    resumeDownload,
    cancelDownload,
    stopSharing,
    deleteFile: deleteFileAction,
    updateSettings,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within AppProvider');
  return context;
}
