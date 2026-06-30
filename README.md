# MeshCDN

MeshCDN is a BitTorrent-inspired Decentralized Swarm-Based Content Distribution Network. It allows users to distribute, discover, and download files over a robust peer-to-peer network without relying on central storage servers.

## Architecture

MeshCDN consists of three primary components that work in tandem:

1. **Tracker (Port 8000)**
   - A central registry built with FastAPI.
   - Maintains a list of active peers, available files, and peer file ownership across the swarm.
   - Used for discovery and network health monitoring.
2. **Peer Node (TCP Port 5000 | UI API Port 5001)**
   - The core Python daemon running on a user's machine.
   - It acts as both a TCP server (Port 5000) to communicate with other peers and exchange chunks, and a FastAPI REST server (Port 5001) providing an interface to the UI.
   - Handles file chunking, hashing, storage, and file reconstruction.
3. **Frontend UI (Port 5173)**
   - A rich, responsive React (Vite) dashboard built to run as a desktop UI.
   - Displays real-time statistics, active downloads, and shared files.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**

## How to Run

To run MeshCDN locally, you need to spin up the three components in separate terminal windows.

### 1. Start the Tracker
```bash
cd backend/tracker
python -m venv .venv
# Activate venv (.venv\Scripts\activate on Windows)
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Start the Peer Node
```bash
cd backend/peer
python -m venv .venv
# Activate venv (.venv\Scripts\activate on Windows)
pip install -r requirements.txt
pip install fastapi uvicorn pydantic # UI API Dependencies
python app/main.py
```

### 3. Start the Frontend UI
```bash
cd frontend
npm install
npm run dev
```

## Important Note on Testing in Browser

Because MeshCDN operates as a local daemon reading directly from your hard drive, it requires the **absolute file path** (e.g. `C:\Users\Me\Desktop\video.mp4`) to share a file. 

If you are running the frontend in a standard web browser (Chrome, Edge, Firefox) rather than a bundled desktop wrapper (like Electron), the browser's security sandbox prevents it from reading absolute file paths via drag-and-drop or the file picker. 

**Workaround:** 
On the `Files` page, use the dedicated text input box. **Paste the absolute file path directly into the input** and hit "Share Path". (On Windows, hold `Shift` + Right-Click the file, select "Copy as path", and paste it into the UI). 

## License
MIT License
