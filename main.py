# main.py
import os
import sys
import tkinter as tk
from src.gui.main_window import MainWindow

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def main():
    # Set up any environment variables or configurations
    os.environ['PYTHONPATH'] = resource_path('src')
    
    # Create and run the application
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
