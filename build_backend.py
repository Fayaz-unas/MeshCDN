import os
import sys
import subprocess

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
FRONTEND_BIN_DIR = os.path.join(ROOT_DIR, "frontend", "binaries")

def run_cmd(cmd, cwd):
    print(f"Running: {' '.join(cmd)} in {cwd}")
    subprocess.check_call(cmd, cwd=cwd)

def main():
    os.makedirs(FRONTEND_BIN_DIR, exist_ok=True)
    
    # 1. Build Tracker
    tracker_dir = os.path.join(ROOT_DIR, "backend", "tracker")
    tracker_pip = os.path.join(tracker_dir, ".venv", "Scripts", "pip.exe" if os.name == "nt" else "bin/pip")
    tracker_py = os.path.join(tracker_dir, ".venv", "Scripts", "python.exe" if os.name == "nt" else "bin/python")
    
    if not os.path.exists(tracker_py):
        print(f"Warning: Virtual environment python not found at {tracker_py}. Falling back to system python.")
        tracker_pip = "pip"
        tracker_py = sys.executable

    sep = ";" if os.name == "nt" else ":"

    print("\n=== Installing PyInstaller in Tracker venv ===")
    run_cmd([tracker_pip, "install", "pyinstaller"], cwd=tracker_dir)
    
    print("\n=== Building Tracker binary (windowless / no console) ===")
    run_cmd([
        tracker_py, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--clean",
        "--paths", ".",
        "--paths", "app",
        f"--add-data=.env{sep}.",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.loops.asyncio",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.http.h11_impl",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=uvicorn.lifespan.off",
        "--distpath", FRONTEND_BIN_DIR,
        "--name", "tracker",
        "app/main.py"
    ], cwd=tracker_dir)

    # 2. Build Peer
    peer_dir = os.path.join(ROOT_DIR, "backend", "peer")
    peer_pip = os.path.join(peer_dir, ".venv", "Scripts", "pip.exe" if os.name == "nt" else "bin/pip")
    peer_py = os.path.join(peer_dir, ".venv", "Scripts", "python.exe" if os.name == "nt" else "bin/python")
    
    if not os.path.exists(peer_py):
        print(f"Warning: Virtual environment python not found at {peer_py}. Falling back to system python.")
        peer_pip = "pip"
        peer_py = sys.executable

    print("\n=== Installing PyInstaller in Peer venv ===")
    run_cmd([peer_pip, "install", "pyinstaller"], cwd=peer_dir)
    
    print("\n=== Building Peer binary (windowless / no console) ===")
    run_cmd([
        peer_py, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--clean",
        "--paths", ".",
        "--paths", "app",
        f"--add-data=app/config{sep}config",
        f"--add-data=app/config{sep}app/config",
        "--hidden-import=services",
        "--hidden-import=routes",
        "--hidden-import=networking",
        "--hidden-import=models",
        "--hidden-import=api",
        "--hidden-import=config",
        "--hidden-import=protocol_handlers",
        "--hidden-import=storage",
        "--hidden-import=uvicorn.logging",
        "--hidden-import=uvicorn.loops",
        "--hidden-import=uvicorn.loops.auto",
        "--hidden-import=uvicorn.loops.asyncio",
        "--hidden-import=uvicorn.protocols",
        "--hidden-import=uvicorn.protocols.http",
        "--hidden-import=uvicorn.protocols.http.auto",
        "--hidden-import=uvicorn.protocols.http.h11_impl",
        "--hidden-import=uvicorn.lifespan",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=uvicorn.lifespan.off",
        "--distpath", FRONTEND_BIN_DIR,
        "--name", "peer",
        "app/main.py"
    ], cwd=peer_dir)
    
    print(f"\n[SUCCESS] Standalone binaries successfully generated in: {FRONTEND_BIN_DIR}")

if __name__ == "__main__":
    main()
