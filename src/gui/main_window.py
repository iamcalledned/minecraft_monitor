# src/gui/main_window.py
import tkinter as tk
from tkinter import messagebox, simpledialog
from src.gui.components import StatusFrame, StatsFrame, ControlFrame
from src.server.manager import ServerManager
from src.server.stats import ServerStats
from src.config import SERVER_HOST, SERVER_USER, SERVER_PORT

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Server Manager")
        self.root.geometry("400x400")

        self.server_manager = ServerManager(SERVER_HOST, SERVER_USER)
        self.server_stats = ServerStats(SERVER_HOST, SERVER_PORT)
        self.last_status = None
        
        self.setup_gui()
        self.connect_to_server()
        self.check_status()

    def setup_gui(self):
        """Set up the GUI components"""
        # Status Frame
        self.status_frame = StatusFrame(self.root)
        self.status_frame.frame.pack(fill='x')

        # Stats Frame
        self.stats_frame = StatsFrame(self.root)
        self.stats_frame.frame.pack(fill='x', pady=10, padx=10)

        # Control Frame
        self.control_frame = ControlFrame(
            self.root,
            start_command=self.start_server,
            stop_command=self.stop_server
        )
        self.control_frame.frame.pack(fill='x')

    def connect_to_server(self):
        """Connect to the server with retry option"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            password = simpledialog.askstring(
                "Password Required", 
                f"Enter password for {SERVER_USER}@{SERVER_HOST}:", 
                show="*"
            )
            
            if not password:
                messagebox.showerror("Error", "Password is required!")
                self.root.quit()
                return

            print(f"Attempting connection (try {retry_count + 1}/{max_retries})...")
            if self.server_manager.connect(password):
                messagebox.showinfo("Success", "Connected to server!")
                return
            
            retry = messagebox.askretrycancel(
                "Connection Failed",
                "Failed to connect to server. Would you like to try again?"
            )
            if not retry:
                self.root.quit()
                return
                
            retry_count += 1
        
        messagebox.showerror("Error", "Maximum connection attempts reached!")
        self.root.quit()

    def check_status(self):
        """Check server status and update GUI"""
        try:
            running = self.server_manager.is_server_running()
            
            # Only update GUI if status changed
            if running != self.last_status:
                self.last_status = running
                if running:
                    self.status_frame.status_label.config(
                        text="Server Status: RUNNING",
                        fg="green"
                    )
                    self.control_frame.start_button.config(state=tk.DISABLED)
                    self.control_frame.stop_button.config(state=tk.NORMAL)
                    self.update_server_stats()
                else:
                    self.status_frame.status_label.config(
                        text="Server Status: STOPPED",
                        fg="red"
                    )
                    self.control_frame.start_button.config(state=tk.NORMAL)
                    self.control_frame.stop_button.config(state=tk.DISABLED)
                    self.clear_stats()
                
        except Exception as e:
            print(f"Status check error: {str(e)}")
            self.status_frame.status_label.config(
                text="Status: ERROR",
                fg="red"
            )

        # Schedule next check
        self.root.after(5000, self.check_status)

   # src/gui/main_window.py
    def update_server_stats(self):
        """Update server statistics display"""
        try:
            if not self.server_manager.is_server_running():
                self.clear_stats()
                return

            # Check if we're in startup mode (server is running but stats show starting)
            startup_mode = (self.status_frame.status_label.cget("text") == "Server Status: STARTING")
            
            # Try to get status with appropriate retry mode
            status = self.server_stats.get_status(startup_mode=startup_mode)
            
            if status:
                # Server is responding, update all stats
                self.status_frame.status_label.config(
                    text="Server Status: RUNNING",
                    fg="green"
                )
                
                # Update version info
                self.stats_frame.version_label.config(
                    text=f"Version: {status.version.name}",
                    fg="green"
                )
                
                # Update player count
                self.stats_frame.players_label.config(
                    text=f"Players: {status.players.online}/{status.players.max}",
                    fg="green" if status.players.online < status.players.max else "orange"
                )
                
                # Update latency
                latency = round(status.latency, 1)
                color = "green" if latency < 100 else "orange" if latency < 200 else "red"
                self.stats_frame.latency_label.config(
                    text=f"Latency: {latency}ms",
                    fg=color
                )

                # Update player list
                self.stats_frame.player_list.delete(1.0, tk.END)
                if status.players.online > 0:
                    if hasattr(status.players, 'sample') and status.players.sample:
                        player_names = [p.name for p in status.players.sample]
                        self.stats_frame.player_list.insert(tk.END, "\n".join(player_names))
                    else:
                        self.stats_frame.player_list.insert(tk.END, f"{status.players.online} player(s) online")
                else:
                    self.stats_frame.player_list.insert(tk.END, "No players online")
            else:
                # Server is running but not responding yet
                if startup_mode:
                    # Still in startup mode, show starting messages
                    self.status_frame.status_label.config(
                        text="Server Status: STARTING",
                        fg="orange"
                    )
                    self.stats_frame.version_label.config(text="Version: Starting...", fg="orange")
                    self.stats_frame.players_label.config(text="Players: Starting...", fg="orange")
                    self.stats_frame.latency_label.config(text="Latency: Starting...", fg="orange")
                    self.stats_frame.player_list.delete(1.0, tk.END)
                    self.stats_frame.player_list.insert(tk.END, "Server is starting...\nThis may take a few minutes...")
                else:
                    # Not in startup mode but server isn't responding
                    self.stats_frame.version_label.config(text="Version: No Response", fg="red")
                    self.stats_frame.players_label.config(text="Players: No Response", fg="red")
                    self.stats_frame.latency_label.config(text="Latency: No Response", fg="red")
                    self.stats_frame.player_list.delete(1.0, tk.END)
                    self.stats_frame.player_list.insert(tk.END, "Waiting for server response...")

        except Exception as e:
            print(f"Failed to update stats: {str(e)}")
            # Don't clear stats immediately if there's an error
            if startup_mode:
                # Still in startup mode
                self.stats_frame.player_list.delete(1.0, tk.END)
                self.stats_frame.player_list.insert(tk.END, "Server is starting...\nThis may take a few minutes...")
            else:
                self.stats_frame.player_list.delete(1.0, tk.END)
                self.stats_frame.player_list.insert(tk.END, "Checking server status...")

    def start_server(self):
        """Handle server start button click"""
        try:
            if self.server_manager.is_server_running():
                messagebox.showinfo("Info", "Server is already running!")
                return

            self.status_frame.status_label.config(text="Starting server...")
            self.control_frame.start_button.config(state=tk.DISABLED)
            
            stdout, stderr = self.server_manager.start_server()
            
            if stderr and stderr.strip():
                raise Exception(f"Start error: {stderr}")
                
            messagebox.showinfo("Success", "Server start command sent!")
            
            # Update GUI to show starting state
            self.status_frame.status_label.config(text="Server Status: STARTING", fg="orange")
            self.stats_frame.version_label.config(text="Version: Starting...", fg="orange")
            self.stats_frame.players_label.config(text="Players: Starting...", fg="orange")
            self.stats_frame.latency_label.config(text="Latency: Starting...", fg="orange")
            self.stats_frame.player_list.delete(1.0, tk.END)
            self.stats_frame.player_list.insert(tk.END, "Server is starting...")
            
            # Force immediate status check
            self.last_status = None
            self.check_status()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {str(e)}")
            self.check_status()

    def stop_server(self):
        """Handle server stop button click"""
        if messagebox.askyesno("Confirm", "Are you sure you want to stop the server?"):
            try:
                self.status_frame.status_label.config(text="Stopping server...")
                self.control_frame.stop_button.config(state=tk.DISABLED)
                
                stdout, stderr = self.server_manager.stop_server()
                
                if stderr and stderr.strip():
                    raise Exception(f"Stop error: {stderr}")
                
                messagebox.showinfo("Success", "Server stop command sent!")
                
                # Force immediate status check
                self.last_status = None
                self.check_status()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop server: {str(e)}")
                self.check_status()

    def clear_stats(self):
        """Clear all statistics displays"""
        self.stats_frame.version_label.config(text="Version: --")
        self.stats_frame.players_label.config(text="Players: --/--")
        self.stats_frame.latency_label.config(text="Latency: --")
        self.stats_frame.player_list.delete(1.0, tk.END)
        self.stats_frame.player_list.insert(tk.END, "Server offline")
