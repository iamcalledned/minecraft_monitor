# src/gui/components.py
import tkinter as tk
from tkinter import ttk

class StatusFrame:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=10)
        
        # Status Label
        self.status_label = tk.Label(
            self.frame,
            text="Server Status: CHECKING...",
            font=("Arial", 12, "bold")
        )
        self.status_label.pack()

class StatsFrame:
    def __init__(self, parent):
        self.frame = tk.LabelFrame(parent, text="Server Statistics")
        self.frame.pack(pady=10, padx=10, fill="x")
        
        # Version Label
        self.version_label = tk.Label(self.frame, text="Version: --")
        self.version_label.pack(anchor="w", padx=5)
        
        # Players Label
        self.players_label = tk.Label(self.frame, text="Players: --/--")
        self.players_label.pack(anchor="w", padx=5)
        
        # Player List
        self.player_list = tk.Text(
            self.frame,
            height=4,
            width=30,
            state="normal"
        )
        self.player_list.pack(pady=5, padx=5)
        self.player_list.insert(tk.END, "No players online")
        
        # Latency Label
        self.latency_label = tk.Label(self.frame, text="Latency: --")
        self.latency_label.pack(anchor="w", padx=5)

class ControlFrame:
    def __init__(self, parent, start_command, stop_command):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=10)
        
        # Start button
        self.start_button = tk.Button(
            self.frame, 
            text="Start Server", 
            command=start_command,
            width=15,
            state=tk.DISABLED
        )
        self.start_button.pack(pady=5)

        # Stop button
        self.stop_button = tk.Button(
            self.frame, 
            text="Stop Server", 
            command=stop_command,
            width=15,
            state=tk.DISABLED
        )
        self.stop_button.pack(pady=5)
