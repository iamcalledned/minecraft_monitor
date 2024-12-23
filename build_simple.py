# build_simple.py
import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'main.py',
    '--name=MinecraftMonitor',
    '--onefile',
    '--windowed',
    '--clean',
    '--noconfirm',
    '--add-data=src;src',
    '--hidden-import=paramiko',
    '--hidden-import=mcstatus',
    '--hidden-import=cryptography',
    '--hidden-import=bcrypt',
    '--hidden-import=nacl',
    '--hidden-import=tkinter'
])
