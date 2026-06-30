import { useMemo } from 'react';
import { useApp } from '../../store/AppContext';
import { formatBytes, formatSpeed, generateSpeedHistory } from '../../utils/helpers';
import { AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, HardDrive, Activity, Database, Clock, Upload, Download, BarChart3, Zap } from 'lucide-react';
import './Statistics.css';

const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#ffffff', border: '1px solid #eaeaea', borderRadius: '8px', padding: '10px 14px', fontSize: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}>
      <div style={{ fontWeight: 600, marginBottom: 8, color: '#111' }}>{label}</div>
      {payload.map((e, i) => (
        <div key={i} style={{ color: e.color, marginBottom: 4 }}>
          {e.name}: {e.name === 'Downloaded' || e.name === 'Uploaded' ? formatBytes(e.value) : formatSpeed(e.value)}
        </div>
      ))}
    </div>
  );
};

export default function Statistics() {
  const { state } = useApp();

  const speedData = useMemo(() => {
    return state.speedHistory.length > 0 ? state.speedHistory : generateSpeedHistory(60);
  }, [state.speedHistory]);

  const storageData = useMemo(() => [
    { name: 'Downloads', value: 12800000000 },
    { name: 'Uploads', value: 8500000000 },
    { name: 'Shared', value: 5200000000 }
  ], []);
  
  const storageColors = ['#0070f3', '#111111', '#64748b'];

  const networkActivityData = useMemo(() => [
    { name: 'Mon', up: 120, down: 230 },
    { name: 'Tue', up: 150, down: 210 },
    { name: 'Wed', up: 200, down: 180 },
    { name: 'Thu', up: 245, down: 189 },
    { name: 'Fri', up: 210, down: 250 },
    { name: 'Sat', up: 180, down: 300 },
    { name: 'Sun', up: 190, down: 280 },
  ], []);

  return (
    <div className="statistics-page">
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-icon green"><HardDrive size={18} /></div>
          <div className="stat-card-value">{state.stats.filesShared || 24}</div>
          <div className="stat-card-label">Files Shared</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon blue"><Download size={18} /></div>
          <div className="stat-card-value">{state.stats.filesDownloaded || 18}</div>
          <div className="stat-card-label">Files Downloaded</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon purple"><TrendingUp size={18} /></div>
          <div className="stat-card-value">{formatBytes(48500000000)}</div>
          <div className="stat-card-label">Total Uploaded</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-icon yellow"><TrendingDown size={18} /></div>
          <div className="stat-card-value">{formatBytes(34200000000)}</div>
          <div className="stat-card-label">Total Downloaded</div>
        </div>
      </div>

      <div className="two-col-grid mt-md">
        <div className="chart-card card">
          <div className="chart-card-title">Download Speed</div>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={speedData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="downloadGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0070f3" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#0070f3" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 0, 0, 0.05)" vertical={false} />
                <XAxis dataKey="time" hide />
                <YAxis hide domain={['dataMin', 'dataMax + 1000']} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="download" name="Download" stroke="#0070f3" strokeWidth={2} fillOpacity={1} fill="url(#downloadGrad)" isAnimationActive={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card card">
          <div className="chart-card-title">Upload Speed</div>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={speedData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <defs>
                  <linearGradient id="uploadGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#64748b" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#64748b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 0, 0, 0.05)" vertical={false} />
                <XAxis dataKey="time" hide />
                <YAxis hide domain={['dataMin', 'dataMax + 1000']} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="upload" name="Upload" stroke="#64748b" strokeWidth={2} fillOpacity={1} fill="url(#uploadGrad)" isAnimationActive={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="two-col-grid mt-md">
        <div className="chart-card card">
          <div className="chart-card-title">Storage Breakdown</div>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={storageData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value }) => `${name} (${formatBytes(value)})`}
                  labelLine={false}
                  stroke="none"
                >
                  {storageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={storageColors[index % storageColors.length]} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card card">
          <div className="chart-card-title">Network Activity (Chunks)</div>
          <div style={{ height: '300px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={networkActivityData} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 0, 0, 0.05)" vertical={false} />
                <XAxis dataKey="name" tick={{ fill: '#666666' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#666666' }} axisLine={false} tickLine={false} />
                <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(0, 0, 0, 0.02)' }} />
                <Bar dataKey="down" name="Downloaded" stackId="a" fill="#0070f3" radius={[0, 0, 4, 4]} />
                <Bar dataKey="up" name="Uploaded" stackId="a" fill="#64748b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="card lifetime-stats mt-md">
        <div className="card-header">
          <div className="card-title">Lifetime Statistics</div>
        </div>
        <div className="two-col-grid" style={{ gap: '40px' }}>
          <div>
            <div className="lifetime-stat-row">
              <span className="detail-label">Files Shared</span>
              <span className="detail-value">24</span>
            </div>
            <div className="lifetime-stat-row">
              <span className="detail-label">Files Downloaded</span>
              <span className="detail-value">18</span>
            </div>
            <div className="lifetime-stat-row">
              <span className="detail-label">Chunks Uploaded</span>
              <span className="detail-value">1,247</span>
            </div>
            <div className="lifetime-stat-row">
              <span className="detail-label">Chunks Downloaded</span>
              <span className="detail-value">892</span>
            </div>
          </div>
          <div>
            <div className="lifetime-stat-row">
              <span className="detail-label">Total Data Uploaded</span>
              <span className="detail-value">45.2 GB</span>
            </div>
            <div className="lifetime-stat-row">
              <span className="detail-label">Total Data Downloaded</span>
              <span className="detail-value">32.1 GB</span>
            </div>
            <div className="lifetime-stat-row">
              <span className="detail-label">Average Download Speed</span>
              <span className="detail-value">4.2 MB/s</span>
            </div>
            <div className="lifetime-stat-row">
              <span className="detail-label">Average Upload Speed</span>
              <span className="detail-value">2.8 MB/s</span>
            </div>
            <div className="lifetime-stat-row">
              <span className="detail-label">Uptime</span>
              <span className="detail-value">47h 23m</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
