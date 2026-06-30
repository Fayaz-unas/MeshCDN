import { useState, useMemo } from 'react';
import { useApp } from '../../store/AppContext';
import { formatRelativeTime, truncateHash } from '../../utils/helpers';
import { Users, Wifi, WifiOff, Eye, X, ShieldAlert } from 'lucide-react';
import './Peers.css';

const hashToColor = (str) => {
  const colors = ['#06d6a0','#4361ee','#7209b7','#f7b731','#ef4444','#38bdf8'];
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
};

export default function Peers() {
  const { state } = useApp();
  const [filter, setFilter] = useState('all');
  const [selectedPeer, setSelectedPeer] = useState(null);

  const allPeers = state.peers || [];
  
  const filteredPeers = useMemo(() => {
    if (filter === 'all') return allPeers;
    return allPeers.filter(p => p.status === filter);
  }, [allPeers, filter]);

  const onlineCount = allPeers.filter(p => p.status === 'online').length;
  const offlineCount = allPeers.length - onlineCount;

  return (
    <div className="peers-page">
      <div className="stats-grid peers-stats">
        <div className="stat-card">
          <div className="stat-card-icon blue"><Users size={18} /></div>
          <div className="stat-card-value">{allPeers.length}</div>
          <div className="stat-card-label">Total Peers</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon green"><Wifi size={18} /></div>
          <div className="stat-card-value">{onlineCount}</div>
          <div className="stat-card-label">Online Peers</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon red"><WifiOff size={18} /></div>
          <div className="stat-card-value">{offlineCount}</div>
          <div className="stat-card-label">Offline Peers</div>
        </div>
      </div>

      <div className="peers-filter tabs mt-md">
        <button className={`tab ${filter === 'all' ? 'active' : ''}`} onClick={() => setFilter('all')}>All</button>
        <button className={`tab ${filter === 'online' ? 'active' : ''}`} onClick={() => setFilter('online')}>Online</button>
        <button className={`tab ${filter === 'offline' ? 'active' : ''}`} onClick={() => setFilter('offline')}>Offline</button>
      </div>

      <div className="peers-grid">
        <div className="card table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Peer</th>
                <th>Status</th>
                <th>IP Address</th>
                <th>Port</th>
                <th>Last Seen</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredPeers.length > 0 ? filteredPeers.map(peer => (
                <tr key={peer.peer_id} onClick={() => setSelectedPeer(peer)} style={{ cursor: 'pointer' }}>
                  <td>
                    <div className="peer-name-cell">
                      <div className={`peer-avatar ${peer.status}`} style={{ backgroundColor: hashToColor(peer.peer_id) }}>
                        {peer.peer_id.replace('peer_', '').substring(0, 2).toUpperCase()}
                      </div>
                      <span className="text-mono">{truncateHash(peer.peer_id, 8)}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${peer.status === 'online' ? 'badge-success' : 'badge-danger'}`}>
                      {peer.status}
                    </span>
                  </td>
                  <td>{peer.ip_address}</td>
                  <td>{peer.port}</td>
                  <td>{formatRelativeTime(peer.last_seen)}</td>
                  <td>
                    <button className="btn btn-sm btn-ghost btn-icon" onClick={(e) => { e.stopPropagation(); setSelectedPeer(peer); }}>
                      <Eye />
                    </button>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="6">
                    <div className="empty-state">
                      <Users size={48} />
                      <h3>No peers connected</h3>
                      <p>Waiting for peers to join the network.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {selectedPeer && (
          <div className="peer-detail-overlay">
            <div className="detail-panel card peer-detail-panel">
              <div className="detail-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div className={`peer-avatar large ${selectedPeer.status}`} style={{ backgroundColor: hashToColor(selectedPeer.peer_id) }}>
                    {selectedPeer.peer_id.replace('peer_', '').substring(0, 2).toUpperCase()}
                  </div>
                  <h3 style={{ fontSize: '15px', fontWeight: 600 }}>Peer Details</h3>
                </div>
                <button className="btn btn-sm btn-ghost btn-icon" onClick={() => setSelectedPeer(null)}>
                  <X />
                </button>
              </div>
              
              <div className="detail-row">
                <span className="detail-label">Peer ID</span>
                <span className="detail-value mono text-sm">{selectedPeer.peer_id}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Installation ID</span>
                <span className="detail-value mono text-sm">{truncateHash(selectedPeer.installation_id, 10)}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Status</span>
                <span className={`badge ${selectedPeer.status === 'online' ? 'badge-success' : 'badge-danger'}`}>
                  {selectedPeer.status}
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">IP Address</span>
                <span className="detail-value">{selectedPeer.ip_address}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Port</span>
                <span className="detail-value">{selectedPeer.port}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Created At</span>
                <span className="detail-value">{new Date(selectedPeer.created_at).toLocaleString()}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Last Seen</span>
                <span className="detail-value">{new Date(selectedPeer.last_seen).toLocaleString()}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
