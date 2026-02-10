import sys
import os
import subprocess

# Ensure src is in the path for imports
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))

def main():
    # Use the specific python version that has tkinter installed
    # We can try to invoke it directly or set PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
    
    # Try to launch using the same logic as src/nodemon/__main__.py
    cmd = [sys.executable, "-m", "nodemon"]
    try:
        subprocess.run(cmd, env=env, check=True, cwd=os.path.dirname(__file__))
    except Exception as e:
        print(f"Error launching via module: {e}")
        # Fallback to direct import if possible
        try:
            sys.path.insert(0, src_path)
            from nodemon.node_demonstrator import main as launch_app
            launch_app()
        except Exception as e2:
            print(f"Error launching via import: {e2}")

if __name__ == "__main__":
    main()
