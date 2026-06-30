import { useMemo } from 'react';
import { useApp } from '../../store/AppContext';
import { formatBytes, formatSpeed, formatRelativeTime, generateSpeedHistory } from '../../utils/helpers';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Users, HardDrive, Download, Upload, CheckCircle, Info, AlertTriangle } from 'lucide-react';
import './Dashboard.css';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#ffffff', border: '1px solid #eaeaea', borderRadius: '8px', padding: '10px 14px', fontSize: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}>
      {payload.map((e, i) => (
        <div key={i} style={{ color: e.color, marginBottom: 2 }}>{e.name === 'download' ? 'Download' : 'Upload'}: {formatSpeed(e.value)}</div>
      ))}
    </div>
  );
};

export default function Dashboard() {
  const { state } = useApp();

  const speedData = useMemo(() => {
    return state.speedHistory?.length > 0 ? state.speedHistory : generateSpeedHistory(60);
  }, [state.speedHistory]);

  const onlinePeersCount = state.peers.filter(p => p.status === 'online').length;
  const activeDownloadsCount = state.downloads.filter(d => d.status !== 'completed').length;

  return (
    <div className="dashboard">

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-icon green"><Users size={18} /></div>
          <div className="stat-card-value">{onlinePeersCount}</div>
          <div className="stat-card-label">Online Peers</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon blue"><Download size={18} /></div>
          <div className="stat-card-value">{activeDownloadsCount}</div>
          <div className="stat-card-label">Active Downloads</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon yellow"><CheckCircle size={18} /></div>
          <div className="stat-card-value">{formatBytes(state.stats.totalDownloaded)}</div>
          <div className="stat-card-label">Total Downloaded</div>
        </div>
      </div>
      <div className="two-col-grid mt-lg" style={{ gridTemplateColumns: '1fr' }}>
        <div className="card dashboard-chart-card">
          <div className="card-header">
            <div className="card-title">Network Throughput</div>
          </div>
          <div style={{ height: '220px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={speedData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorDownload" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0070f3" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#0070f3" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorUpload" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#64748b" stopOpacity={0.1} />
                    <stop offset="95%" stopColor="#64748b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 0, 0, 0.05)" vertical={false} />
                <XAxis dataKey="time" hide />
                <YAxis hide domain={['dataMin', 'dataMax + 1000']} />
                <Tooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="download" stroke="#0070f3" strokeWidth={2} fillOpacity={1} fill="url(#colorDownload)" isAnimationActive={false} />
                <Area type="monotone" dataKey="upload" stroke="#64748b" strokeWidth={2} fillOpacity={1} fill="url(#colorUpload)" isAnimationActive={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
