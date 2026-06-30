// MeshCDN API Service Layer
// Centralized API calls to the Tracker (port 8000) and Peer (port 5000)

const TRACKER_URL = 'http://localhost:8000';
const PEER_URL = 'http://localhost:5001';

class ApiService {
  // ─── Tracker: Health ───────────────────────────
  async getTrackerStatus() {
    try {
      const res = await fetch(`${TRACKER_URL}/health`);
      if (!res.ok) throw new Error('Tracker unhealthy');
      return { online: true, data: await res.json() };
    } catch {
      return { online: false, data: null };
    }
  }

  // ─── Tracker: Peers ────────────────────────────
  async getPeers() {
    const res = await fetch(`${TRACKER_URL}/peers`);
    if (!res.ok) throw new Error('Failed to fetch peers');
    return res.json();
  }

  // ─── Tracker: Files ────────────────────────────
  async getFiles() {
    const res = await fetch(`${TRACKER_URL}/files`);
    if (!res.ok) throw new Error('Failed to fetch files');
    return res.json();
  }

  async getFile(fileHash) {
    const res = await fetch(`${TRACKER_URL}/files/${fileHash}`);
    if (!res.ok) throw new Error('File not found');
    return res.json();
  }

  async deleteFile(fileHash) {
    const res = await fetch(`${TRACKER_URL}/files/${fileHash}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete file');
    return res.json();
  }

  // ─── Tracker: Peer File States ─────────────────
  async getPeerFileStates(peerId) {
    const res = await fetch(`${TRACKER_URL}/peer-file-states/peer/${peerId}`);
    if (!res.ok) throw new Error('Failed to fetch peer file states');
    return res.json();
  }

  async getFilePeers(fileHash) {
    const res = await fetch(`${TRACKER_URL}/peer-file-states/file/${fileHash}`);
    if (!res.ok) throw new Error('Failed to fetch file peers');
    return res.json();
  }

  // ─── Tracker: Swarm ────────────────────────────
  async getSwarm(fileHash) {
    const res = await fetch(`${TRACKER_URL}/swarms/${fileHash}`);
    if (!res.ok) throw new Error('Swarm not found');
    return res.json();
  }

  // ─── Peer: Share File ──────────────────────────
  async shareFile(filePath) {
    const res = await fetch(`${PEER_URL}/share`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_path: filePath }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to share file');
    }
    return res.json();
  }

  // ─── Peer: Download File ───────────────────────
  async downloadFile(fileHash) {
    const res = await fetch(`${PEER_URL}/download`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_hash: fileHash }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Failed to start download');
    }
    return res.json();
  }

  // ─── Peer: Get Shared Files ────────────────────
  async getSharedFiles() {
    try {
      const res = await fetch(`${PEER_URL}/shared-files`);
      if (!res.ok) return [];
      return res.json();
    } catch {
      return [];
    }
  }

  // ─── Peer: Stop Sharing ────────────────────────
  async stopSharing(fileHash) {
    const res = await fetch(`${PEER_URL}/stop-sharing/${fileHash}`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to stop sharing');
    return res.json();
  }

  // ─── Peer: Status ──────────────────────────────
  async getPeerStatus() {
    try {
      const res = await fetch(`${PEER_URL}/status`);
      if (!res.ok) throw new Error('Peer offline');
      return { online: true, data: await res.json() };
    } catch {
      return { online: false, data: null };
    }
  }
}

export const api = new ApiService();
export { TRACKER_URL, PEER_URL };
