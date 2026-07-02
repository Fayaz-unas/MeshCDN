import { createContext, useContext, useReducer, useCallback, useRef, useEffect } from 'react';

// ─── LocalStorage Helper ─────────────────────────
const loadSavedSettings = () => {
  try {
    const saved = localStorage.getItem('meshcdn_settings');
    if (saved) return JSON.parse(saved);
  } catch {}
  return {};
};

// ─── Initial State ───────────────────────────────
const initialState = {
  // Connection Status
  trackerOnline: true,
  peerOnline: true,

  // Data
  files: [
    {
      id: 1,
      file_name: 'ubuntu-24.04-desktop-amd64.iso',
      file_hash: 'a1b2c3d4e5f6789012345678',
      file_size: 5242880000,
      total_chunks: 5000,
      chunk_size: 1048576,
      mime_type: 'application/x-iso9660-image',
      created_at: new Date(Date.now() - 3600000 * 24).toISOString()
    },
    {
      id: 2,
      file_name: 'blender-4.1.0-windows-x64.zip',
      file_hash: 'f6e5d4c3b2a1098765432109',
      file_size: 314572800,
      total_chunks: 300,
      chunk_size: 1048576,
      mime_type: 'application/zip',
      created_at: new Date(Date.now() - 3600000 * 5).toISOString()
    },
    {
      id: 3,
      file_name: 'project-presentation-demo.mp4',
      file_hash: '9876543210abcdef01234567',
      file_size: 47185920,
      total_chunks: 45,
      chunk_size: 1048576,
      mime_type: 'video/mp4',
      created_at: new Date(Date.now() - 3600000 * 2).toISOString()
    }
  ],
  peers: [
    {
      peer_id: 'node_us_east_01',
      installation_id: 'inst_88a9c0d1',
      status: 'online',
      ip_address: '192.168.1.104',
      port: 5001,
      created_at: new Date(Date.now() - 86400000 * 10).toISOString(),
      last_seen: new Date(Date.now() - 10000).toISOString()
    },
    {
      peer_id: 'node_eu_central_04',
      installation_id: 'inst_33b2e7f9',
      status: 'online',
      ip_address: '10.0.0.45',
      port: 5002,
      created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
      last_seen: new Date(Date.now() - 25000).toISOString()
    },
    {
      peer_id: 'node_ap_south_02',
      installation_id: 'inst_55c1a4b8',
      status: 'offline',
      ip_address: '172.16.0.88',
      port: 5003,
      created_at: new Date(Date.now() - 86400000 * 20).toISOString(),
      last_seen: new Date(Date.now() - 3600000 * 4).toISOString()
    }
  ],
  downloads: [],
  activities: [],
  notifications: [],

  // Stats
  stats: {
    totalUploaded: 1258291200,
    totalDownloaded: 4508876800,
    filesShared: 3,
    filesDownloaded: 12,
    chunksUploaded: 1200,
    chunksDownloaded: 4300,
    storageUsed: 5604618240,
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
  ADD_ACTIVITY: 'ADD_ACTIVITY',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION',
  UPDATE_SPEED: 'UPDATE_SPEED',
  UPDATE_SETTINGS: 'UPDATE_SETTINGS',
  SET_SEARCH_QUERY: 'SET_SEARCH_QUERY',
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
    } catch {}
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

  // Standalone Status Refresh
  const refreshStatus = useCallback(() => {
    dispatch({ type: ActionTypes.SET_TRACKER_STATUS, payload: true });
    dispatch({ type: ActionTypes.SET_PEER_STATUS, payload: true });
  }, []);

  const refreshFiles = useCallback(() => {}, []);
  const refreshPeers = useCallback(() => {}, []);
  const refreshAll = useCallback(() => {
    refreshStatus();
  }, [refreshStatus]);

  // Actions
  const shareFile = useCallback(async (filePath) => {
    const fileName = filePath.split(/[\\/]/).pop() || filePath;
    const newFile = {
      id: Date.now(),
      file_name: fileName,
      file_hash: 'hash_' + Math.random().toString(36).substring(2, 10),
      file_size: Math.floor(Math.random() * 50000000) + 1000000,
      total_chunks: 10,
      chunk_size: 1048576,
      mime_type: 'application/octet-stream',
      created_at: new Date().toISOString(),
      path: filePath
    };
    dispatch({ type: ActionTypes.SET_FILES, payload: [newFile, ...stateRef.current.files] });
    addNotification('success', 'File Shared', `Successfully shared file`);
    addActivity('success', `Shared file`);
    return { success: true, data: newFile };
  }, [addNotification, addActivity]);

  const downloadFile = useCallback(async (fileHash) => {
    const id = Date.now();
    const targetFile = stateRef.current.files.find(f => f.file_hash === fileHash);
    const fileName = targetFile ? targetFile.file_name : `file_${fileHash.slice(0, 6)}.dat`;
    
    dispatch({
      type: ActionTypes.ADD_DOWNLOAD,
      payload: {
        id,
        fileHash,
        fileName,
        progress: 0,
        speed: 1024 * 500,
        peers: 3,
        eta: '30s',
        status: 'downloading',
        startedAt: Date.now(),
      },
    });
    addActivity('info', `Download started`);

    const interval = setInterval(() => {
      const currentDl = stateRef.current.downloads?.find((d) => d.id === id);
      if (!currentDl || currentDl.status === 'cancelled' || currentDl.status === 'completed' || currentDl.status === 'failed' || currentDl.status === 'paused') {
        if (currentDl?.status === 'cancelled' || currentDl?.status === 'completed' || currentDl?.status === 'failed') {
          clearInterval(interval);
        }
        return;
      }

      const nextProgress = Math.min(100, (currentDl.progress || 0) + 20);
      if (nextProgress >= 100) {
        clearInterval(interval);
        dispatch({
          type: ActionTypes.UPDATE_DOWNLOAD,
          payload: { id, progress: 100, status: 'completed', eta: 'Done', speed: 0 },
        });
        addNotification('success', 'Download Complete', `File downloaded successfully`);
        addActivity('success', `Download completed`);
      } else {
        dispatch({
          type: ActionTypes.UPDATE_DOWNLOAD,
          payload: { id, progress: nextProgress, speed: 1024 * 600, eta: `${Math.round((100 - nextProgress) / 20 * 1)}s` },
        });
      }
    }, 500);
  }, [addNotification, addActivity]);

  const pauseDownload = useCallback((id) => {
    dispatch({ type: ActionTypes.UPDATE_DOWNLOAD, payload: { id, status: 'paused', speed: 0, eta: 'Paused' } });
    addNotification('info', 'Download Paused', 'Download has been paused');
  }, [addNotification]);

  const resumeDownload = useCallback((id) => {
    dispatch({ type: ActionTypes.UPDATE_DOWNLOAD, payload: { id, status: 'downloading', eta: 'Resuming...' } });
    addNotification('success', 'Download Resumed', 'Download has resumed');
  }, [addNotification]);

  const cancelDownload = useCallback((id) => {
    dispatch({
      type: ActionTypes.UPDATE_DOWNLOAD,
      payload: { id, status: 'cancelled', eta: 'Cancelled', speed: 0 },
    });
    addNotification('warning', 'Download Cancelled', 'The download was cancelled.');
  }, [addNotification]);

  const stopSharing = useCallback((fileHash) => {
    addNotification('success', 'Stopped Sharing', 'File is no longer shared');
    addActivity('info', 'Stopped sharing file');
  }, [addNotification, addActivity]);

  const deleteFileAction = useCallback((fileHash) => {
    dispatch({
      type: ActionTypes.SET_FILES,
      payload: stateRef.current.files.filter(f => f.file_hash !== fileHash)
    });
    addNotification('success', 'File Deleted', 'File removed from network');
    addActivity('info', 'Deleted file');
  }, [addNotification, addActivity]);

  const updateSettings = useCallback((newSettings) => {
    dispatch({ type: ActionTypes.UPDATE_SETTINGS, payload: newSettings });
  }, []);

  // Initial refresh on mount
  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

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

