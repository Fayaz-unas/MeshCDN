import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { useApp } from '../../store/AppContext';
import NotificationContainer from '../Notifications/NotificationContainer';
import {
  LayoutDashboard,
  FolderOpen,
  Download,
  Users,
  BarChart3,
  Settings,
  Search,
  Bell,
  HardDrive,
  Hexagon,
  Sun,
  Moon,
} from 'lucide-react';
import { useEffect } from 'react';
import { formatBytes } from '../../utils/helpers';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/files', icon: FolderOpen, label: 'Files' },
  { path: '/downloads', icon: Download, label: 'Downloads' },
  { path: '/peers', icon: Users, label: 'Peers' },
  { path: '/statistics', icon: BarChart3, label: 'Statistics' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

const pageInfo = {
  '/': { title: 'Dashboard', subtitle: 'System overview & health' },
  '/files': { title: 'Files', subtitle: 'Manage shared & downloaded files' },
  '/downloads': { title: 'Downloads', subtitle: 'Active & completed transfers' },
  '/peers': { title: 'Peers', subtitle: 'Connected network peers' },
  '/statistics': { title: 'Statistics', subtitle: 'Network performance & metrics' },
  '/settings': { title: 'Settings', subtitle: 'Application configuration' },
  '/developer': { title: 'Developer', subtitle: 'Protocol internals & debugging' },
};

export default function Layout() {
  const { state, dispatch, ActionTypes } = useApp();
  const location = useLocation();
  const currentPage = pageInfo[location.pathname] || { title: 'MeshCDN', subtitle: '' };

  const onlinePeers = state.peers.filter((p) => p.status === 'online').length;

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', state.settings.darkMode ? 'dark' : 'light');
  }, [state.settings.darkMode]);

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="sidebar-brand-icon">
              <Hexagon size={20} />
            </div>
            <div className="sidebar-brand-text">
              <h1>MeshCDN</h1>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              end={item.path === '/'}
            >
              <item.icon />
              <span>{item.label}</span>
              {item.path === '/downloads' && state.downloads.filter(d => d.status !== 'completed').length > 0 && (
                <span className="nav-item-badge">
                  {state.downloads.filter(d => d.status !== 'completed').length}
                </span>
              )}
              {item.path === '/peers' && onlinePeers > 0 && (
                <span className="nav-item-badge">{onlinePeers}</span>
              )}
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <header className="main-header" style={{ justifyContent: 'center', gap: '16px' }}>
          {/* Search */}
          <div className="header-search" style={{ width: '100%', maxWidth: '600px' }}>
            <Search />
            <input
              type="text"
              placeholder="Search files, peers..."
              value={state.searchQuery}
              onChange={(e) =>
                dispatch({ type: ActionTypes.SET_SEARCH_QUERY, payload: e.target.value })
              }
            />
          </div>
          
          <button
            className="header-btn"
            onClick={() => dispatch({ 
              type: ActionTypes.UPDATE_SETTINGS, 
              payload: { darkMode: !state.settings.darkMode } 
            })}
            title={state.settings.darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            {state.settings.darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </header>

        {/* Page Content */}
        <div className="page-content">
          <Outlet />
        </div>
      </div>

      {/* Notifications */}
      <NotificationContainer />
    </div>
  );
}
