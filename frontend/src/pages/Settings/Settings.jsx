import { useState } from 'react';
import { useApp } from '../../store/AppContext';
import { Settings as SettingsIcon, HardDrive, Gauge } from 'lucide-react';
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
              <div className="setting-label">Ask Where to Save Each File</div>
              <div className="setting-description">Prompt for destination after each download instead of saving to default folder directly</div>
            </div>
            <label className="toggle">
              <input 
                type="checkbox" 
                checked={state.settings.askBeforeDownload ?? true} 
                onChange={(e) => updateSettings({ askBeforeDownload: e.target.checked })} 
              />
              <span className="toggle-slider"></span>
            </label>
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
        </div>

        <div className="card settings-section">
          <div className="settings-section-title">
            <SettingsIcon className="section-icon" /> General
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

      </div>
    </div>
  );
}
