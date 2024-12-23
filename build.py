# build.py
import PyInstaller.__main__
import os
import sys

def build():
    # Get the directory containing the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define icon path (create an .ico file and put it in the project root)
    icon_path = os.path.join(script_dir, 'minecraft_monitor.ico')
    
    PyInstaller.__main__.run([
        'main.py',  # Your main script
        '--name=MinecraftMonitor',  # Name of the executable
        '--onefile',  # Create a single executable file
        '--windowed',  # Don't show console window
        f'--icon={icon_path}',  # Application icon
        '--add-data=src;src',  # Include the src directory
        '--clean',  # Clean cache
        '--noconfirm',  # Replace existing spec/build
        # Add required hidden imports
        '--hidden-import=paramiko',
        '--hidden-import=mcstatus',
        '--hidden-import=cryptography'
    ])

if __name__ == "__main__":
    build()
