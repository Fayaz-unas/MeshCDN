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

  Sun,
  Moon,
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { formatBytes } from '../../utils/helpers';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/files', icon: FolderOpen, label: 'Files' },
  { path: '/downloads', icon: Download, label: 'Downloads' },
  { path: '/peers', icon: Users, label: 'Peers' },
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

const MeshLogo = ({ size = 24 }) => (
  <svg 
    width={size} 
    height={size} 
    viewBox="0 0 32 32" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
    style={{ filter: 'drop-shadow(0 0 8px rgba(67, 97, 238, 0.4))' }}
  >
    {/* Connections */}
    <path d="M6 22L6 12L16 18L26 12L26 22" stroke="#4361ee" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M6 12L16 6L26 12" stroke="#4bc0c8" strokeWidth="1.5" strokeDasharray="2 3" strokeLinecap="round" />
    <path d="M6 22L16 28L26 22" stroke="#4bc0c8" strokeWidth="1.5" strokeDasharray="2 3" strokeLinecap="round" />
    <path d="M16 6L16 18" stroke="#4bc0c8" strokeWidth="1.5" strokeDasharray="2 3" strokeLinecap="round" />
    <path d="M16 18L16 28" stroke="#4bc0c8" strokeWidth="1.5" strokeDasharray="2 3" strokeLinecap="round" />
    
    {/* Nodes */}
    <circle cx="6" cy="22" r="3" fill="#4361ee" />
    <circle cx="6" cy="12" r="3" fill="#4361ee" />
    <circle cx="16" cy="18" r="3.5" fill="#4bc0c8" />
    <circle cx="26" cy="12" r="3" fill="#4361ee" />
    <circle cx="26" cy="22" r="3" fill="#4361ee" />
    <circle cx="16" cy="6" r="2.5" fill="#4bc0c8" />
    <circle cx="16" cy="28" r="2.5" fill="#4bc0c8" />
  </svg>
);

export default function Layout() {
  const { state, dispatch, ActionTypes } = useApp();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();
  const currentPage = pageInfo[location.pathname] || { title: 'MeshCDN', subtitle: '' };

  const onlinePeers = state.peers.filter((p) => p.status === 'online').length;

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', state.settings.darkMode ? 'dark' : 'light');
  }, [state.settings.darkMode]);

  return (
    <div className={`app-layout ${isCollapsed ? 'sidebar-collapsed' : ''}`}>
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="sidebar-brand-icon">
              <MeshLogo size={32} />
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
