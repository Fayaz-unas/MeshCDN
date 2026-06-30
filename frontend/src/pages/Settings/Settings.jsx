import { useState } from 'react';
import { useApp } from '../../store/AppContext';
import { Settings as SettingsIcon, Globe, HardDrive, Gauge, Code2, Save, Info } from 'lucide-react';
import './Settings.css';

export default function Settings() {
  const { state, updateSettings } = useApp();
  const handleChange = (key, value) => {
    updateSettings({ [key]: value });
  };

  return (
    <div className="settings-page">
      <div className="settings-container">
        
        <div className="card settings-section">
          <div className="settings-section-title">
            <Globe className="section-icon" /> Network
          </div>
          <div className="setting-row">
            <div>
              <div className="setting-label">Tracker URL</div>
              <div className="setting-description">The central tracker for peer discovery</div>
            </div>
            <input 
              type="text" 
              className="form-input setting-input" 
              value={state.settings.trackerUrl} 
              onChange={(e) => handleChange('trackerUrl', e.target.value)} 
            />
          </div>
          <div className="setting-row">
            <div>
              <div className="setting-label">Peer Port</div>
              <div className="setting-description">TCP port for peer-to-peer connections</div>
            </div>
            <input 
              type="number" 
              className="form-input setting-input" 
              value={state.settings.peerPort} 
              onChange={(e) => handleChange('peerPort', parseInt(e.target.value) || 5000)} 
            />
          </div>
        </div>

        <div className="card settings-section">
          <div className="settings-section-title">
            <HardDrive className="section-icon" /> Storage
          </div>
          <div className="setting-row">
            <div>
              <div className="setting-label">Download Folder</div>
              <div className="setting-description">Where completed downloads are saved</div>
            </div>
            <input 
              type="text" 
              className="form-input setting-input" 
              value={state.settings.downloadFolder} 
              onChange={(e) => handleChange('downloadFolder', e.target.value)} 
            />
          </div>
          <div className="setting-row">
            <div>
              <div className="setting-label">Upload Folder</div>
              <div className="setting-description">Directory for shared files</div>
            </div>
            <input 
              type="text" 
              className="form-input setting-input" 
              value={state.settings.uploadFolder} 
              onChange={(e) => handleChange('uploadFolder', e.target.value)} 
            />
          </div>
        </div>

        <div className="card settings-section">
          <div className="settings-section-title">
            <Gauge className="section-icon" /> Bandwidth
          </div>
          <div className="setting-row">
            <div>
              <div className="setting-label">Maximum Upload Speed</div>
              <div className="setting-description">Limit upload bandwidth (0 = unlimited)</div>
            </div>
            <div className="input-with-suffix">
              <input 
                type="number" 
                className="form-input setting-input" 
                value={state.settings.maxUploadSpeed} 
                onChange={(e) => handleChange('maxUploadSpeed', parseInt(e.target.value) || 0)} 
              />
              <span className="suffix">KB/s</span>
            </div>
          </div>
          <div className="setting-row">
            <div>
              <div className="setting-label">Maximum Download Speed</div>
              <div className="setting-description">Limit download bandwidth (0 = unlimited)</div>
            </div>
            <div className="input-with-suffix">
              <input 
                type="number" 
                className="form-input setting-input" 
                value={state.settings.maxDownloadSpeed} 
                onChange={(e) => handleChange('maxDownloadSpeed', parseInt(e.target.value) || 0)} 
              />
              <span className="suffix">KB/s</span>
            </div>
          </div>
          <div className="setting-row">
            <div>
              <div className="setting-label">Chunk Size</div>
              <div className="setting-description">Size of data chunks in bytes</div>
            </div>
            <div className="input-with-suffix">
              <input 
                type="number" 
                className="form-input setting-input" 
                value={state.settings.chunkSize} 
                onChange={(e) => handleChange('chunkSize', parseInt(e.target.value) || 1048576)} 
              />
              <span className="suffix">Bytes</span>
            </div>
          </div>
        </div>

        <div className="card settings-section">
          <div className="settings-section-title">
            <SettingsIcon className="section-icon" /> General
          </div>
          <div className="setting-row">
            <div>
              <div className="setting-label">Auto Start</div>
              <div className="setting-description">Start MeshCDN when system boots</div>
            </div>
            <label className="toggle">
              <input 
                type="checkbox" 
                checked={state.settings.autoStart} 
                onChange={(e) => handleChange('autoStart', e.target.checked)} 
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
          <div className="setting-row">
            <div>
              <div className="setting-label">Dark Mode</div>
              <div className="setting-description">Use dark theme appearance</div>
            </div>
            <label className="toggle">
              <input 
                type="checkbox" 
                checked={state.settings.darkMode} 
                onChange={(e) => updateSettings({ darkMode: e.target.checked })} 
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div className={`card settings-section ${state.settings.developerMode ? 'dev-mode-active' : ''}`}>
          <div className="settings-section-title">
            <Code2 className="section-icon" /> Developer
          </div>
          <div className="setting-row">
            <div>
              <div className="setting-label">Developer Mode</div>
              <div className="setting-description">Enable advanced protocol inspection and debugging tools</div>
            </div>
            <label className="toggle">
              <input 
                type="checkbox" 
                checked={state.settings.developerMode} 
                onChange={(e) => handleChange('developerMode', e.target.checked)} 
              />
              <span className="toggle-slider"></span>
            </label>
          </div>
        </div>


      </div>
    </div>
  );
}
