import sys
import os
import subprocess

# This script is located in src/launch.py
# We want to run it from the root directory context
def main():
    # Path to the src directory relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    src_path = current_dir

    env = os.environ.copy()
    # Add src to PYTHONPATH so 'nodemon' module can be found
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
    
    # Try to launch using python -m nodemon
    cmd = [sys.executable, "-m", "nodemon"]
    try:
        # Run from project root to keep paths consistent
        subprocess.run(cmd, env=env, check=True, cwd=project_root)
    except Exception as e:
        print(f"Error launching via module: {e}")
        # Fallback to direct import
        try:
            if src_path not in sys.path:
                sys.path.insert(0, src_path)
            from nodemon.node_demonstrator import main as launch_app
            launch_app()
        except Exception as e2:
            print(f"Error launching via import: {e2}")

if __name__ == "__main__":
    main()
