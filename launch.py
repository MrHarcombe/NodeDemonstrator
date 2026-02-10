import tkinter as tk
import sys
import os

# Ensure src is in the path for imports
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Based on the file structure, let's try to import the main application class
try:
    from nodemon.node_demonstrator import NodeDemonstrator
except ImportError as e:
    print(f"Import error: {e}")
    NodeDemonstrator = None

def main():
    # If using ttkbootstrap as seen in pyproject.toml
    try:
        import ttkbootstrap as ttk
        root = ttk.Window(title="NodeDemonstrator", themename="litera")
    except ImportError:
        root = tk.Tk()
        root.title("NodeDemonstrator")
    
    root.geometry("1000x800")
    
    if NodeDemonstrator:
        try:
            # Most Tkinter apps take the root window as the first argument
            app = NodeDemonstrator(root)
        except Exception as e:
            print(f"Error launching: {e}")
            label = tk.Label(root, text=f"NodeDemonstrator Launch Error: {e}")
            label.pack(pady=20)
    else:
        label = tk.Label(root, text="Could not find NodeDemonstrator component.\nPlease check your file structure.")
        label.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    main()
