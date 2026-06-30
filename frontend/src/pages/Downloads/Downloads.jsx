import { useState } from 'react';
import { useApp } from '../../store/AppContext';
import { formatBytes, formatSpeed, formatDuration } from '../../utils/helpers';
import { Download, Pause, Play, X, Plus, ArrowDown, CheckCircle, Clock, AlertCircle, Loader } from 'lucide-react';
import './Downloads.css';

const statusConfig = {
  downloading: { label: 'Downloading', badge: 'info', icon: ArrowDown },
  completed:   { label: 'Completed',   badge: 'success', icon: CheckCircle },
  connecting:  { label: 'Connecting',  badge: 'warning', icon: Loader },
  paused:      { label: 'Paused',      badge: 'warning', icon: Pause },
  error:       { label: 'Error',       badge: 'danger', icon: AlertCircle },
};



const tabs = [
  { key: 'all',       label: 'All' },
  { key: 'active',    label: 'Active' },
  { key: 'completed', label: 'Completed' },
];

export default function Downloads() {
  const { state, downloadFile, pauseDownload, resumeDownload, cancelDownload, addNotification } = useApp();

  const [activeTab, setActiveTab] = useState('active');
  const [showModal, setShowModal] = useState(false);
  const [hashInput, setHashInput] = useState('');

  const allDownloads = state.downloads || [];

  // Filter by tab
  const filteredDownloads = allDownloads.filter((d) => {
    if (activeTab === 'all') return true;
    if (activeTab === 'active') return d.status === 'downloading' || d.status === 'connecting' || d.status === 'paused';
    if (activeTab === 'completed') return d.status === 'completed';
    return true;
  });

  // Counts for tab badges
  const activeCount = allDownloads.filter((d) => d.status === 'downloading' || d.status === 'connecting' || d.status === 'paused').length;
  const completedCount = allDownloads.filter((d) => d.status === 'completed').length;

  const handleDownload = () => {
    if (!hashInput.trim()) return;
    downloadFile(hashInput.trim());
    setHashInput('');
    setShowModal(false);
    addNotification('info', 'Download Started', 'Connecting to peers...');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleDownload();
  };

  return (
    <>
      <div className="downloads-header">
        <div className="downloads-header-left">
          <div className="downloads-summary" style={{ margin: 0 }}>
            <button
              className={`downloads-summary-stat ${activeTab === 'all' ? 'active-tab' : ''}`}
              onClick={() => setActiveTab('all')}
            >
              <Download size={14} />
              <span>All:</span>
              <span className="stat-value">{allDownloads.length}</span>
            </button>
            <button
              className={`downloads-summary-stat active ${activeTab === 'active' ? 'active-tab' : ''}`}
              onClick={() => setActiveTab('active')}
            >
              <ArrowDown size={14} />
              <span>Active:</span>
              <span className="stat-value">{activeCount}</span>
            </button>
            <button
              className={`downloads-summary-stat completed ${activeTab === 'completed' ? 'active-tab' : ''}`}
              onClick={() => setActiveTab('completed')}
            >
              <CheckCircle size={14} />
              <span>Completed:</span>
              <span className="stat-value">{completedCount}</span>
            </button>
          </div>
        </div>

        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <Plus size={16} />
          Download File
        </button>
      </div>

      {/* Downloads List */}
      {filteredDownloads.length > 0 ? (
        <div className="downloads-list">
          {filteredDownloads.map((download) => {
            const config = statusConfig[download.status] || statusConfig.downloading;
            const StatusIcon = config.icon;

            return (
              <div key={download.id} className={`download-card ${download.status}`}>
                <div className="download-card-header">
                  <div>
                    <div className="download-card-name">
                      {download.fileName || download.fileHash}
                    </div>
                    <div className="download-card-hash">{download.fileHash}</div>
                  </div>
                  <span className={`badge badge-${config.badge}`}>
                    <StatusIcon size={12} />
                    {config.label}
                  </span>
                </div>

                <div className="progress-bar">
                  <div
                    className={`progress-bar-fill ${download.status === 'downloading' ? 'animated' : ''}`}
                    style={{ width: `${download.progress}%` }}
                  />
                </div>

                <div className="download-card-stats">
                  <span>{download.progress}%</span>
                  <span>
                    <ArrowDown size={13} />
                    {formatSpeed(download.speed)}
                  </span>
                  <span>{download.peers} peers</span>
                  <span>
                    <Clock size={13} />
                    {download.status === 'completed' ? 'Completed' : formatDuration(download.eta)}
                  </span>
                </div>

                <div className="download-card-actions">
                  {download.status === 'downloading' && (
                    <button className="btn btn-sm btn-ghost" onClick={() => pauseDownload(download.id, download.fileHash)}>
                      <Pause size={14} /> Pause
                    </button>
                  )}
                  {download.status === 'paused' && (
                    <button className="btn btn-sm btn-ghost" onClick={() => resumeDownload(download.id, download.fileHash)}>
                      <Play size={14} /> Resume
                    </button>
                  )}
                  {download.status !== 'completed' && download.status !== 'cancelled' && (
                    <button className="btn btn-sm btn-danger" onClick={() => cancelDownload(download.id, download.fileHash)}>
                      <X size={14} /> Cancel
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="downloads-empty">
          <div className="downloads-empty-icon">
            <Download />
          </div>
          <h3>No downloads found</h3>
          <p>
            {activeTab === 'completed'
              ? 'You haven\'t completed any downloads yet.'
              : activeTab === 'active'
              ? 'No active downloads at the moment.'
              : 'Start downloading files from the mesh network by clicking the button above.'}
          </p>
        </div>
      )}

      {/* Download Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal download-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Start Download</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">File Hash</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Enter the file hash to download..."
                  value={hashInput}
                  onChange={(e) => setHashInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  autoFocus
                />
                <p className="form-hint">
                  Paste the unique hash of the file you want to download from the mesh network.
                </p>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setShowModal(false)}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleDownload}
                disabled={!hashInput.trim()}
              >
                <Download size={16} />
                Download
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
