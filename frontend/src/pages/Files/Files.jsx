import { useState, useRef, useCallback, useEffect } from 'react';
import { useApp } from '../../store/AppContext';
import { formatBytes, truncateHash, getFileTypeInfo, copyToClipboard } from '../../utils/helpers';
import { Upload, FolderOpen, Copy, StopCircle, Trash2, Eye, FileText, X, MoreVertical, ExternalLink, Search, Plus } from 'lucide-react';
import './Files.css';

export default function Files() {
  const { state, shareFile, stopSharing, deleteFile, addNotification, dispatch, ActionTypes } = useApp();
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [contextMenu, setContextMenu] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [pathInput, setPathInput] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const allFiles = state.files || [];
  
  const filteredFiles = allFiles.filter(f => 
    f.file_name?.toLowerCase().includes((state.searchQuery || '').toLowerCase())
  );

  const handleShare = () => {
    if (!pathInput.trim()) return;
    shareFile(pathInput.trim().replace(/^"|"$/g, ''));
    setPathInput('');
    setShowModal(false);
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      shareFile(file.path || file.name);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      shareFile(file.path || file.name);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleContextMenu = (e, file) => {
    e.preventDefault();
    setContextMenu({
      x: e.clientX,
      y: e.clientY,
      file
    });
  };

  const closeContextMenu = useCallback(() => {
    setContextMenu(null);
  }, []);

  useEffect(() => {
    document.addEventListener('click', closeContextMenu);
    return () => {
      document.removeEventListener('click', closeContextMenu);
    };
  }, [closeContextMenu]);

  const handleCopyHash = (hash, e) => {
    e?.stopPropagation();
    copyToClipboard(hash);
    addNotification('success', 'Copied', 'File hash copied to clipboard');
  };

  return (
    <>
      <div className="files-page">
      

      <div 
        className={`drop-zone ${isDragging ? 'active' : ''}`}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <Upload />
        <h3>Drop files here to share</h3>
        
        <div style={{ marginTop: '24px', display: 'flex', gap: '16px', justifyContent: 'center' }} onClick={(e) => e.stopPropagation()}>
          <button className="btn btn-secondary" onClick={() => fileInputRef.current?.click()}>
            <FolderOpen size={16} /> Browse Local Files
          </button>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={16} /> Enter Absolute Path
          </button>
        </div>
        
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          onChange={handleFileSelect}
        />
      </div>

      <div className="files-grid mt-md">
        <div className="card table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>File</th>
                <th>Size</th>
                <th>Type</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredFiles.length > 0 ? filteredFiles.map(file => {
                const typeInfo = getFileTypeInfo(file.file_name, file.mime_type);
                return (
                  <tr 
                    key={file.id || file.file_hash} 
                    onClick={() => setSelectedFile(file)}
                    onContextMenu={(e) => handleContextMenu(e, file)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td>
                      <div className="file-name-cell">
                        <div className="file-type-dot" style={{ backgroundColor: typeInfo.color }}></div>
                        <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{file.file_name}</span>
                      </div>
                    </td>
                    <td>{formatBytes(file.file_size)}</td>
                    <td>
                      <span className="badge" style={{ backgroundColor: `${typeInfo.color}20`, color: typeInfo.color }}>
                        {typeInfo.label}
                      </span>
                    </td>
                    <td>
                      <span className="badge badge-success">Sharing</span>
                    </td>
                    <td>
                      <div className="file-actions">
                        <button className="btn btn-sm btn-ghost btn-icon" onClick={(e) => handleCopyHash(file.file_hash, e)} title="Copy Hash">
                          <Copy />
                        </button>
                        <button className="btn btn-sm btn-ghost btn-icon" onClick={(e) => { e.stopPropagation(); stopSharing(file.file_hash); }} title="Stop Sharing">
                          <StopCircle />
                        </button>
                        <button className="btn btn-sm btn-danger btn-icon" onClick={(e) => { e.stopPropagation(); deleteFile(file.file_hash); }} title="Delete">
                          <Trash2 />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              }) : (
                <tr>
                  <td colSpan="5">
                    <div className="empty-state">
                      <FolderOpen size={48} />
                      <h3>No files found</h3>
                      <p>Try adjusting your search or share a new file.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {selectedFile && (
          <div className="file-detail-overlay">
            <div className="detail-panel card">
              <div className="detail-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3 style={{ fontSize: '15px', fontWeight: 600 }}>File Details</h3>
                <button className="btn btn-sm btn-ghost btn-icon" onClick={() => setSelectedFile(null)}>
                  <X />
                </button>
              </div>
              
              <div className="detail-row">
                <span className="detail-label">File Name</span>
                <span className="detail-value">{selectedFile.file_name}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">File Hash</span>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span className="detail-value mono">{truncateHash(selectedFile.file_hash, 12)}</span>
                  <button className="btn btn-sm btn-ghost btn-icon" style={{ padding: '2px' }} onClick={() => handleCopyHash(selectedFile.file_hash)}>
                    <Copy size={12}/>
                  </button>
                </div>
              </div>
              <div className="detail-row">
                <span className="detail-label">Size</span>
                <span className="detail-value">{formatBytes(selectedFile.file_size)}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Total Chunks</span>
                <span className="detail-value">{selectedFile.total_chunks}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Chunk Size</span>
                <span className="detail-value">{formatBytes(selectedFile.chunk_size)}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">MIME Type</span>
                <span className="detail-value">{selectedFile.mime_type || 'Unknown'}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Created At</span>
                <span className="detail-value">{new Date(selectedFile.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {contextMenu && (
        <div 
          className="context-menu" 
          style={{ top: contextMenu.y, left: contextMenu.x }}
          onClick={(e) => e.stopPropagation()}
        >
          <button className="context-menu-item" onClick={() => { handleCopyHash(contextMenu.file.file_hash); closeContextMenu(); }}>
            <Copy /> Copy Hash
          </button>
          <div className="context-menu-divider"></div>
          <button className="context-menu-item" onClick={() => { stopSharing(contextMenu.file.file_hash); closeContextMenu(); }}>
            <StopCircle /> Stop Sharing
          </button>
          <button className="context-menu-item danger" onClick={() => { deleteFile(contextMenu.file.file_hash); closeContextMenu(); }}>
            <Trash2 /> Delete File
          </button>
        </div>
      )}
    </div>

      {/* Share Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal download-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Share File</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Absolute File Path</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. C:\Users\Name\Desktop\file.mp4"
                  value={pathInput}
                  onChange={(e) => setPathInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleShare()}
                  autoFocus
                />
                <p className="form-hint">
                  Enter the absolute path of the file on your local machine to share it with the network.
                </p>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setShowModal(false)}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                onClick={handleShare}
                disabled={!pathInput.trim()}
              >
                <Upload size={16} />
                Share
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
