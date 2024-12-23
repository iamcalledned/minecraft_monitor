# src/server/stats.py
from mcstatus import JavaServer
import time
import socket

class ServerStats:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = JavaServer(host, port)
        self.startup_retries = 30  # Try for 30 * 2 = 60 seconds during startup
        self.normal_retries = 3    # Normal operation retries

    def get_status(self, startup_mode=False):
        """
        Get server status with retry logic
        startup_mode: If True, use more retries and longer delays for server startup
        """
        max_retries = self.startup_retries if startup_mode else self.normal_retries
        retry_delay = 2  # seconds between retries
        
        for attempt in range(max_retries):
            try:
                status = self.server.status()
                if status:
                    return status
            except (socket.timeout, ConnectionRefusedError) as e:
                print(f"Status check attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
            except Exception as e:
                print(f"Unexpected error in status check: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        return None

    def get_query(self):
        """Get detailed server query (if enabled)"""
        try:
            return self.server.query()
        except Exception as e:
            print(f"Query failed: {str(e)}")
            return None
