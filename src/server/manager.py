# src/server/manager.py
import paramiko
from paramiko import SSHClient, AutoAddPolicy
import os

class ServerManager:
    def __init__(self, host, user):
        self.host = host
        self.user = user
        self.ssh = None
        
        # Create .ssh directory if it doesn't exist
        ssh_dir = os.path.expanduser('~/.ssh')
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir)
            
        # Create known_hosts file if it doesn't exist
        known_hosts = os.path.join(ssh_dir, 'known_hosts')
        if not os.path.exists(known_hosts):
            open(known_hosts, 'a').close()

    def connect(self, password):
        """Establish SSH connection to the server"""
        try:
            self.ssh = SSHClient()
            self.ssh.set_missing_host_key_policy(AutoAddPolicy())
            
            print(f"Attempting to connect to {self.host}...")
            self.ssh.connect(
                hostname=self.host,
                username=self.user,
                password=password,
                timeout=30,
                allow_agent=False,
                look_for_keys=False
            )
            print("Successfully connected to server")
            return True
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False

    def execute_command(self, command):
        """Execute a command on the remote server"""
        try:
            if not self.ssh:
                raise Exception("No SSH connection")
            print(f"Executing command: {command}")
            stdin, stdout, stderr = self.ssh.exec_command(command, timeout=10)
            stdout_str = stdout.read().decode()
            stderr_str = stderr.read().decode()
            print(f"stdout: {stdout_str}")
            print(f"stderr: {stderr_str}")
            return stdout_str, stderr_str
        except Exception as e:
            print(f"Command execution error: {str(e)}")
            return None, str(e)

    def cleanup_screens(self):
        """Clean up multiple screen sessions"""
        try:
            # First, try to detach from any attached screens
            self.execute_command("screen -d minecraft")
            
            # Get list of minecraft screens
            stdout, _ = self.execute_command("screen -list | grep minecraft")
            if stdout:
                # Kill all minecraft screen sessions
                self.execute_command("pkill -f 'SCREEN.*minecraft'")
                # Clean up dead screens
                self.execute_command("screen -wipe")
        except Exception as e:
            print(f"Screen cleanup error: {str(e)}")

    def stop_server(self):
        """Stop the Minecraft server"""
        try:
            print("Attempting to stop server...")
            
            if not self.is_server_running():
                return "Server is not running", ""
            
            # Send stop command to all possible screen sessions
            commands = [
                "screen -S minecraft -X stuff 'stop\n'",
                "screen -r minecraft -X stuff 'stop\n'",
                "screen -d minecraft",  # Detach from screen if attached
                f"pkill -f 'java.*paper.jar'"  # Fallback: kill Java process directly
            ]
            
            output = []
            errors = []
            
            for cmd in commands:
                stdout, stderr = self.execute_command(cmd)
                if stdout:
                    output.append(stdout)
                if stderr:
                    errors.append(stderr)
            
            # Clean up screens after stopping
            self.cleanup_screens()
            
            return "\n".join(output), "\n".join(errors)
            
        except Exception as e:
            print(f"Stop server error: {str(e)}")
            return None, str(e)

    def start_server(self):
        """Start the Minecraft server"""
        try:
            print("Attempting to start server...")
            
            # Clean up any existing screens first
            self.cleanup_screens()
            
            if self.is_server_running():
                return "Server is already running", ""
            
            # Start the server in a new screen session
            cmd = "cd /home/minecraft/minecraft && screen -dmS minecraft java -Xms4G -Xmx4G -jar paper.jar --nogui"
            stdout, stderr = self.execute_command(cmd)
            
            return stdout, stderr
            
        except Exception as e:
            print(f"Start server error: {str(e)}")
            return None, str(e)

    def is_server_running(self):
        """Check if server is running"""
        try:
            # Use a more reliable command combination
            cmd = "ps aux | grep -v grep | grep 'java.*paper.jar' || true"
            stdout, _ = self.execute_command(cmd)
            return bool(stdout and 'paper.jar' in stdout)
        except Exception as e:
            print(f"Server status check error: {str(e)}")
            return False

    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.ssh:
            self.ssh.close()
