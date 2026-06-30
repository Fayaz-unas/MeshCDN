import { useState, useMemo } from 'react';
import { useApp } from '../../store/AppContext';
import { truncateHash, formatBytes } from '../../utils/helpers';
import { Terminal, Layers, Globe, Activity, Code, Trash2, Copy } from 'lucide-react';
import { copyToClipboard } from '../../utils/helpers';
import './Developer.css';

export default function Developer() {
  const { state } = useApp();
  const [activeTab, setActiveTab] = useState('protocol');

  const demoMessages = useMemo(() => [
    { id:1, time:'10:30:01.234', dir:'out', type:'HELLO', payload:'{"peer_id":"peer_586b735ad8d9"}' },
    { id:2, time:'10:30:01.256', dir:'in', type:'WELCOME', payload:'{}' },
    { id:3, time:'10:30:05.102', dir:'out', type:'REQUEST_CHUNK', payload:'{"file_hash":"4d226e9a...","chunk_index":0}' },
    { id:4, time:'10:30:05.892', dir:'in', type:'CHUNK_DATA', payload:'{"chunk_index":0,"size":1048576}' },
    { id:5, time:'10:30:06.001', dir:'out', type:'REQUEST_CHUNK', payload:'{"chunk_index":1}' },
    { id:6, time:'10:30:06.734', dir:'in', type:'CHUNK_DATA', payload:'{"chunk_index":1,"size":1048576}' },
    { id:7, time:'10:31:01.000', dir:'out', type:'PING', payload:'{}' },
    { id:8, time:'10:31:01.023', dir:'in', type:'PONG', payload:'{}' },
    { id:9, time:'10:31:30.100', dir:'out', type:'REQUEST_CHUNK', payload:'{"chunk_index":2}' },
    { id:10, time:'10:31:30.550', dir:'in', type:'CHUNK_NOT_FOUND', payload:'{"reason":"Chunk not found."}' },
  ], []);

  const demoTransfers = useMemo(() => [
    { chunk_index: 0, file_hash: '4d226e9a...', peer_id: 'peer_112233...', dir: '↓', size: 1048576, status: 'Success', time: '10:30:05' },
    { chunk_index: 1, file_hash: '4d226e9a...', peer_id: 'peer_aabbcc...', dir: '↓', size: 1048576, status: 'Success', time: '10:30:06' },
    { chunk_index: 2, file_hash: '4d226e9a...', peer_id: 'peer_112233...', dir: '↓', size: 0, status: 'Failed', time: '10:31:30' },
    { chunk_index: 5, file_hash: 'b7ae48c1...', peer_id: 'peer_f7e8d9...', dir: '↑', size: 1048576, status: 'Success', time: '10:32:15' },
  ], []);

  const getMsgTypeClass = (type) => {
    if (['HELLO', 'WELCOME'].includes(type)) return 'type-green';
    if (['REQUEST_CHUNK', 'CHUNK_DATA'].includes(type)) return 'type-blue';
    if (['CHUNK_NOT_FOUND', 'ERROR'].includes(type)) return 'type-red';
    return 'type-gray';
  };

  const chunkGrid = Array.from({ length: 100 }, (_, i) => ({
    id: i,
    available: Math.random() > 0.2
  }));

  const handleCopyRaw = () => {
    copyToClipboard(JSON.stringify(state, null, 2));
  };

  return (
    <div className="dev-page">
      <div className="tabs">
        <button className={`tab ${activeTab === 'protocol' ? 'active' : ''}`} onClick={() => setActiveTab('protocol')}>
          <Terminal size={14} style={{ marginRight: '6px', display: 'inline' }}/> Protocol Messages
        </button>
        <button className={`tab ${activeTab === 'transfers' ? 'active' : ''}`} onClick={() => setActiveTab('transfers')}>
          <Activity size={14} style={{ marginRight: '6px', display: 'inline' }}/> Chunk Transfers
        </button>
        <button className={`tab ${activeTab === 'swarm' ? 'active' : ''}`} onClick={() => setActiveTab('swarm')}>
          <Globe size={14} style={{ marginRight: '6px', display: 'inline' }}/> Swarm State
        </button>
        <button className={`tab ${activeTab === 'raw' ? 'active' : ''}`} onClick={() => setActiveTab('raw')}>
          <Code size={14} style={{ marginRight: '6px', display: 'inline' }}/> Raw Data
        </button>
      </div>

      <div className="tab-content mt-md">
        {activeTab === 'protocol' && (
          <div className="card protocol-card">
            <div className="card-header" style={{ marginBottom: 0, paddingBottom: '16px', borderBottom: '1px solid var(--border-color)' }}>
              <div className="card-title">TCP Protocol Log</div>
              <button className="btn btn-sm btn-ghost"><Trash2 size={14} /> Clear Log</button>
            </div>
            <div className="protocol-log">
              {demoMessages.map(msg => (
                <div key={msg.id} className="protocol-msg">
                  <span className="msg-time">{msg.time}</span>
                  <span className={`msg-dir ${msg.dir === 'in' ? 'in' : 'out'}`}>{msg.dir === 'in' ? '←' : '→'}</span>
                  <span className={`msg-type ${getMsgTypeClass(msg.type)}`}>{msg.type.padEnd(15)}</span>
                  <span className="msg-payload">{msg.payload}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'transfers' && (
          <div className="card table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Dir</th>
                  <th>Chunk</th>
                  <th>File Hash</th>
                  <th>Peer ID</th>
                  <th>Size</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {demoTransfers.map((t, i) => (
                  <tr key={i}>
                    <td>{t.time}</td>
                    <td style={{ color: t.dir === '↓' ? 'var(--accent-primary)' : 'var(--accent-secondary)' }}>{t.dir}</td>
                    <td>{t.chunk_index}</td>
                    <td className="text-mono">{t.file_hash}</td>
                    <td className="text-mono">{t.peer_id}</td>
                    <td>{formatBytes(t.size)}</td>
                    <td>
                      <span className={`badge ${t.status === 'Success' ? 'badge-success' : 'badge-danger'}`}>
                        {t.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'swarm' && (
          <div className="card">
            <div className="card-header">
              <div className="card-title">Global Chunk Map Visualization</div>
            </div>
            <p className="text-muted text-sm mb-md">Representing availability across all connected peers in swarm.</p>
            <div className="chunk-grid">
              {chunkGrid.map(cell => (
                <div 
                  key={cell.id} 
                  className={`chunk-cell ${cell.available ? 'available' : 'missing'}`} 
                  title={`Chunk ${cell.id}: ${cell.available ? 'Available' : 'Missing'}`}
                />
              ))}
            </div>
            <div style={{ display: 'flex', gap: '16px', marginTop: '16px', fontSize: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div className="chunk-cell available"></div> Available (80%)
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <div className="chunk-cell missing"></div> Missing (20%)
              </div>
            </div>
          </div>
        )}

        {activeTab === 'raw' && (
          <div className="card">
            <div className="card-header">
              <div className="card-title">Application State Dump</div>
              <button className="btn btn-sm btn-ghost" onClick={handleCopyRaw}><Copy size={14} /> Copy JSON</button>
            </div>
            <pre className="raw-json">
              {JSON.stringify(state, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
