import sys
import os
import subprocess

# This script is located in src/launch.py
def main():
    # Use the system python that has tkinter installed
    # In Replit's Nix environment, /usr/bin/python3 usually has the system packages
    python_exe = "/usr/bin/python3"
    if not os.path.exists(python_exe):
        python_exe = sys.executable

    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    src_path = current_dir

    env = os.environ.copy()
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
    
    # Force DISPLAY for X11/VNC
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"
    
    cmd = [python_exe, "-m", "nodemon"]
    try:
        subprocess.run(cmd, env=env, check=True, cwd=project_root)
    except Exception as e:
        print(f"Error launching: {e}")
        # Fallback to current executable
        try:
            subprocess.run([sys.executable, "-m", "nodemon"], env=env, check=True, cwd=project_root)
        except Exception as e2:
            print(f"Fallback error: {e2}")

if __name__ == "__main__":
    main()
