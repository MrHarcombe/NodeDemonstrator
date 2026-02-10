import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Tkinter App")
    root.geometry("300x200")
    
    label = tk.Label(root, text="Hello, Tkinter!")
    label.pack(pady=20)
    
    button = tk.Button(root, text="Quit", command=root.quit)
    button.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    main()
