import sys
import os
import subprocess

def main():
    # In Replit's Nix environment, we need to ensure we use the correct python
    # that has the system-installed tkinter (from nixpkgs).
    python_exe = sys.executable

    # src/launch.py is in the src directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    src_path = current_dir

    env = os.environ.copy()
    # Ensure the 'src' directory is in PYTHONPATH so 'nodemon' is a valid package
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
    
    # Force DISPLAY for X11/VNC (standard for Replit VNC)
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"
    
    # We use -m nodemon to run the package. 
    # The __main__.py in src/nodemon will call node_demonstrator.main()
    cmd = [python_exe, "-m", "nodemon"]
    
    try:
        # Running with check=True to catch immediate failures
        subprocess.run(cmd, env=env, check=True, cwd=project_root)
    except subprocess.CalledProcessError as e:
        print(f"Application exited with error code {e.returncode}")
    except Exception as e:
        print(f"Failed to launch application: {e}")

if __name__ == "__main__":
    main()
