import { createContext, useContext, useReducer, useCallback, useRef, useEffect } from 'react';
import { api } from '../services/api';

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
    try {
      const id = Date.now();
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
      const result = await api.downloadFile(fileHash);
      dispatch({
        type: ActionTypes.UPDATE_DOWNLOAD,
        payload: { id, progress: 100, status: 'completed', eta: 'Done' },
      });
      addNotification('success', 'Download Complete', `File downloaded successfully`);
      addActivity('success', `Download completed`);
      await refreshFiles();
      return result;
    } catch (err) {
      addNotification('error', 'Download Failed', err.message);
      throw err;
    }
  }, [addNotification, addActivity, refreshFiles]);

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
