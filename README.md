# 🌐 MeshCDN

> **A BitTorrent-inspired Decentralized Swarm-Based Content Distribution Network built with Python, FastAPI, React, Vite, and Electron.**

MeshCDN empowers users to distribute, discover, and download files over a robust peer-to-peer (P2P) network without relying on central storage servers. By breaking files into cryptographically verified chunks and distributing them across an active swarm, MeshCDN maximizes bandwidth efficiency and network resilience.

---

## ✨ Key Features

- **🚀 Decentralized Swarm Distribution:** High-performance chunk-based P2P file sharing over custom TCP protocols.
- **🔒 Cryptographic Chunk Verification:** Automatic SHA-256 chunk hashing and real-time integrity verification during swarm downloads to prevent corruption or tampering.
- **📡 Centralized Discovery Tracker:** A lightweight FastAPI registry that tracks active peers, swarm health, and file ownership across the network without storing actual file contents.
- **🖥️ Modern Hybrid UI:** A responsive React + Vite dashboard packaged with Electron for native desktop capabilities (system tray, direct filesystem access, and download prompts).
- **⚙️ Granular Peer Controls:** Configure TCP/API ports, manage download prompt preferences, and monitor swarm connectivity in real time.

---

## 📚 Technical Architecture & Handbooks

MeshCDN is accompanied by exhaustive technical documentation detailing every layer of the system. For deep dives into system internals, protocols, sequence diagrams, and class references, consult our comprehensive architecture handbooks:

| Handbook | Description |
| :--- | :--- |
| **[📘 Peer Architecture Handbook](./PEER_ARCHITECTURE.md)** | Comprehensive technical reference for the Python peer daemon. Covers the TCP networking engine, chunking/hashing algorithms, protocol handlers, SQLite storage layer, and lifecycle management. |
| **[📗 Tracker Architecture Handbook](./TRACKER_ARCHITECTURE.md)** | Detailed guide for the FastAPI tracker registry. Covers database schemas, background health monitoring, peer eviction policies, and REST discovery endpoints. |

---

## 🏗️ Core Components

MeshCDN operates as a triad of decoupled components working synchronously:

```
+-----------------------------------------------------------------+
|                        MeshCDN Network                          |
+-----------------------------------------------------------------+
                                |
                   +------------v------------+
                   |   Tracker Server        |
                   |   FastAPI (Port 8000)   |
                   +----+---------------+----+
                        |               |
         Peer Discovery |               | Peer Discovery
         & Heartbeats   |               | & Heartbeats
                        |               |
         +--------------v----+     +----v--------------+
         | Peer Node A       |<--->| Peer Node B       |
         | TCP: 5000         | P2P | TCP: 5000         |
         | UI API: 5001      |     | UI API: 5001      |
         +--------^----------+     +-------------------+
                  |
         REST API | (Localhost)
                  |
         +--------v----------+
         | Frontend UI       |
         | React / Electron  |
         | (Port 3000)       |
         +-------------------+
```

1. **Tracker Server (Port 8000)**
   - Built with **FastAPI** and **SQLAlchemy/SQLite**.
   - Acts as the central swarm registry, maintaining active peers, available files, and chunk distributions.
   - Executes background health checks and evicts stale peers automatically.

2. **Peer Node Daemon (TCP Port 5000 | UI REST API Port 5001)**
   - The core **Python** daemon running locally on each participant's machine.
   - **TCP Server (Port 5000):** Connects with remote peers in the swarm to request, exchange, and verify file chunks.
   - **REST API Server (Port 5001):** Provides a clean localhost interface for the frontend UI to trigger downloads, share files, and fetch real-time transfer stats.
   - Manages local file chunking, SHA-256 verification, and file reassembly.

3. **Frontend UI (Port 3000 / Desktop App)**
   - A modern **React (Vite)** application wrapped in **Electron**.
   - Displays available network files, swarm peers, download progress, and activity logs.
   - Decoupled architecture allows it to run as a native desktop client or in a standard web browser.

---

## 🛠️ Prerequisites

Ensure you have the following installed before running MeshCDN:
- **Python 3.10+**
- **Node.js 18+** & **npm**

---

## 🚀 Getting Started

To launch the complete MeshCDN suite locally, open three separate terminal windows and follow the steps below:

### 1️⃣ Start the Tracker Server
The tracker must be running first so peers can register and discover one another.

```bash
cd backend/tracker
python -m venv .venv

# Activate virtual environment:
# Windows (PowerShell): .\.venv\Scripts\Activate.ps1
# Windows (CMD):        .\.venv\Scripts\activate.bat
# Linux / macOS:        source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2️⃣ Start the Peer Node Daemon
Start the local peer node that handles P2P sharing and UI communication.

```bash
cd backend/peer
python -m venv .venv

# Activate virtual environment:
# Windows (PowerShell): .\.venv\Scripts\Activate.ps1
# Windows (CMD):        .\.venv\Scripts\activate.bat
# Linux / macOS:        source .venv/bin/activate

pip install -r requirements.txt
python app/main.py
```

### 3️⃣ Start the Frontend UI
You can run the UI as a native Electron desktop application (recommended) or in a web browser:

```bash
cd frontend
npm install

# Option A: Run as Native Electron Desktop App (Recommended)
npm run electron:dev

# Option B: Run in Web Browser Mode (Vite Dev Server on Port 3000)
npm run dev

# Option C: Build Production Desktop Application
npm run electron:build
```

---

## ⚠️ Important Note on Sharing Files & Browser Sandboxing

Because MeshCDN operates as a local daemon reading directly from your disk, it requires the **absolute file path** (e.g., `C:\Users\Username\Desktop\video.mp4` or `/home/user/video.mp4`) to chunk and share a file with the swarm.

- **Using Electron Desktop App:** The Electron client provides native OS filesystem access, allowing seamless file sharing and path resolution.
- **Using Standard Web Browsers (Chrome, Edge, Firefox):** Standard web browsers enforce strict security sandboxes that prevent web pages from retrieving absolute file paths via drag-and-drop or standard file pickers.
  - **Workaround:** On the **Files** page in browser mode, use the dedicated text input box. **Paste the absolute file path directly into the input field** and click **"Share Path"**.
  - *Tip for Windows:* Hold `Shift` + Right-Click on your file in File Explorer, select **"Copy as path"**, and paste it directly into the UI (remove surrounding quotes if necessary).

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for details.
