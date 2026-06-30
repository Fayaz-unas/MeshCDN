// Format bytes to human readable
export function formatBytes(bytes, decimals = 1) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(decimals))} ${sizes[i]}`;
}

// Format speed (bytes/sec)
export function formatSpeed(bytesPerSec) {
  if (!bytesPerSec || bytesPerSec === 0) return '0 B/s';
  return `${formatBytes(bytesPerSec)}/s`;
}

// Format time duration
export function formatDuration(seconds) {
  if (!seconds || seconds <= 0) return '—';
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${Math.round(seconds % 60)}s`;
  return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
}

// Format relative time (e.g., "2 min ago")
export function formatRelativeTime(dateStr) {
  if (!dateStr) return 'Never';
  const now = new Date();
  const date = new Date(dateStr);
  const diff = Math.floor((now - date) / 1000);

  if (diff < 5) return 'Just now';
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

// Truncate hash for display
export function truncateHash(hash, chars = 8) {
  if (!hash) return '—';
  if (hash.length <= chars * 2) return hash;
  return `${hash.slice(0, chars)}...${hash.slice(-chars)}`;
}

// Get file type icon name based on extension or mime type
export function getFileTypeInfo(fileName, mimeType) {
  const ext = fileName?.split('.').pop()?.toLowerCase();
  const types = {
    // Video
    mp4: { label: 'Video', color: '#f97316' },
    mkv: { label: 'Video', color: '#f97316' },
    avi: { label: 'Video', color: '#f97316' },
    mov: { label: 'Video', color: '#f97316' },
    webm: { label: 'Video', color: '#f97316' },
    // Audio
    mp3: { label: 'Audio', color: '#8b5cf6' },
    flac: { label: 'Audio', color: '#8b5cf6' },
    wav: { label: 'Audio', color: '#8b5cf6' },
    ogg: { label: 'Audio', color: '#8b5cf6' },
    // Image
    png: { label: 'Image', color: '#06d6a0' },
    jpg: { label: 'Image', color: '#06d6a0' },
    jpeg: { label: 'Image', color: '#06d6a0' },
    gif: { label: 'Image', color: '#06d6a0' },
    webp: { label: 'Image', color: '#06d6a0' },
    svg: { label: 'Image', color: '#06d6a0' },
    // Document
    pdf: { label: 'PDF', color: '#ef4444' },
    doc: { label: 'Document', color: '#4361ee' },
    docx: { label: 'Document', color: '#4361ee' },
    txt: { label: 'Text', color: '#8892b0' },
    // Archive
    zip: { label: 'Archive', color: '#f7b731' },
    rar: { label: 'Archive', color: '#f7b731' },
    '7z': { label: 'Archive', color: '#f7b731' },
    tar: { label: 'Archive', color: '#f7b731' },
    gz: { label: 'Archive', color: '#f7b731' },
    // Code / Disk Image
    iso: { label: 'Disk Image', color: '#38bdf8' },
    img: { label: 'Disk Image', color: '#38bdf8' },
    exe: { label: 'Executable', color: '#ef4444' },
  };

  return types[ext] || { label: 'File', color: '#8892b0' };
}

// Copy to clipboard
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // Fallback
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    return true;
  }
}

// Generate mock speed data for demo
export function generateSpeedHistory(points = 60) {
  const data = [];
  let dl = 0;
  let ul = 0;
  for (let i = 0; i < points; i++) {
    dl = Math.max(0, dl + (Math.random() - 0.45) * 500000);
    ul = Math.max(0, ul + (Math.random() - 0.48) * 300000);
    data.push({
      time: Date.now() - (points - i) * 2000,
      download: Math.round(dl),
      upload: Math.round(ul),
    });
  }
  return data;
}
