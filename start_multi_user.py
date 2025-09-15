#!/usr/bin/env python3
"""
Multi-User King's Choice Management - Production Start Script

This script handles:
- Background process management
- Automatic dependency installation
- Process monitoring and restart
- Graceful shutdown
- Log management
"""

import os
import sys
import subprocess
import signal
import time
import psutil
import json
from datetime import datetime
from pathlib import Path

class MultiUserAppManager:
    def __init__(self):
        self.app_dir = Path(__file__).parent
        self.pid_file = self.app_dir / "app.pid"
        self.log_file = self.app_dir / "logs" / "app.log"
        self.error_log = self.app_dir / "logs" / "error.log"
        self.config_file = self.app_dir / "app_config.json"
        self.port = 5000
        self.host = "0.0.0.0"
        
        # Create logs directory
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        default_config = {
            "port": 5000,
            "host": "0.0.0.0",
            "workers": 1,
            "auto_restart": True,
            "max_restarts": 5,
            "restart_delay": 5
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
        
        self.port = self.config.get("port", 5000)
        self.host = self.config.get("host", "0.0.0.0")
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("📦 Installing dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, cwd=self.app_dir)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def setup_database(self):
        """Setup the multi-user database system"""
        print("🗄️ Setting up database...")
        try:
            subprocess.run([
                sys.executable, "setup_multi_user.py"
            ], check=True, cwd=self.app_dir)
            print("✅ Database setup completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Database setup failed: {e}")
            return False
    
    def is_running(self):
        """Check if the application is running"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists and is our app
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                if "python" in process.name().lower() and "app.py" in " ".join(process.cmdline()):
                    return True
            
            # Clean up stale PID file
            self.pid_file.unlink()
            return False
        except:
            return False
    
    def get_pid(self):
        """Get the current process ID"""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    return int(f.read().strip())
            except:
                return None
        return None
    
    def start_app(self, background=True):
        """Start the application"""
        if self.is_running():
            print("⚠️ Application is already running")
            return True
        
        print("🚀 Starting King's Choice Management Multi-User System...")
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Setup database if needed
        if not self.setup_database():
            return False
        
        try:
            if background:
                # Start in background
                with open(self.log_file, 'a') as log_f, open(self.error_log, 'a') as err_f:
                    process = subprocess.Popen([
                        sys.executable, "app.py"
                    ], stdout=log_f, stderr=err_f, cwd=self.app_dir)
                
                # Save PID
                with open(self.pid_file, 'w') as f:
                    f.write(str(process.pid))
                
                # Wait a moment and check if it started
                time.sleep(3)
                
                if self.is_running():
                    print(f"✅ Application started successfully (PID: {process.pid})")
                    print(f"🌐 Access at: http://{self.host}:{self.port}")
                    print(f"📝 Logs: {self.log_file}")
                    print(f"❌ Error logs: {self.error_log}")
                    return True
                else:
                    print("❌ Application failed to start")
                    return False
            else:
                # Start in foreground
                subprocess.run([sys.executable, "app.py"], cwd=self.app_dir)
                return True
                
        except Exception as e:
            print(f"❌ Failed to start application: {e}")
            return False
    
    def stop_app(self):
        """Stop the application"""
        if not self.is_running():
            print("⚠️ Application is not running")
            return True
        
        pid = self.get_pid()
        if not pid:
            print("⚠️ No PID file found")
            return True
        
        print(f"🛑 Stopping application (PID: {pid})...")
        
        try:
            process = psutil.Process(pid)
            
            # Try graceful shutdown first
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
                print("✅ Application stopped gracefully")
            except psutil.TimeoutExpired:
                # Force kill if still running
                print("⚠️ Force killing application...")
                process.kill()
                process.wait(timeout=5)
                print("✅ Application force stopped")
            
            # Clean up PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            return True
            
        except psutil.NoSuchProcess:
            print("⚠️ Process not found, cleaning up PID file")
            if self.pid_file.exists():
                self.pid_file.unlink()
            return True
        except Exception as e:
            print(f"❌ Failed to stop application: {e}")
            return False
    
    def restart_app(self):
        """Restart the application"""
        print("🔄 Restarting application...")
        self.stop_app()
        time.sleep(2)
        return self.start_app()
    
    def status(self):
        """Show application status"""
        if self.is_running():
            pid = self.get_pid()
            try:
                process = psutil.Process(pid)
                memory = process.memory_info().rss / 1024 / 1024  # MB
                cpu = process.cpu_percent()
                uptime = datetime.now() - datetime.fromtimestamp(process.create_time())
                
                print("✅ Application Status: RUNNING")
                print(f"   PID: {pid}")
                print(f"   Memory: {memory:.1f} MB")
                print(f"   CPU: {cpu:.1f}%")
                print(f"   Uptime: {uptime}")
                print(f"   URL: http://{self.host}:{self.port}")
                
                # Check if port is accessible
                try:
                    import requests
                    response = requests.get(f"http://{self.host}:{self.port}", timeout=5)
                    if response.status_code == 200:
                        print("   Health: ✅ OK")
                    else:
                        print("   Health: ⚠️ Not responding properly")
                except:
                    print("   Health: ❌ Not accessible")
                    
            except Exception as e:
                print(f"✅ Application Status: RUNNING (PID: {pid})")
                print(f"   Details: {e}")
        else:
            print("❌ Application Status: NOT RUNNING")
        
        print(f"📝 Logs: {self.log_file}")
        print(f"❌ Error logs: {self.error_log}")
    
    def logs(self, lines=50):
        """Show application logs"""
        print(f"📝 Last {lines} lines of logs:")
        print("=" * 50)
        
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                all_lines = f.readlines()
                for line in all_lines[-lines:]:
                    print(line.rstrip())
        else:
            print("No log file found")
    
    def monitor(self):
        """Monitor the application and restart if needed"""
        print("👀 Starting application monitor...")
        print("Press Ctrl+C to stop monitoring")
        
        restart_count = 0
        max_restarts = self.config.get("max_restarts", 5)
        
        try:
            while True:
                if not self.is_running():
                    print(f"⚠️ Application stopped, restarting... (attempt {restart_count + 1})")
                    
                    if restart_count >= max_restarts:
                        print(f"❌ Maximum restart attempts ({max_restarts}) reached")
                        break
                    
                    if self.start_app():
                        restart_count += 1
                        print(f"✅ Application restarted (restart count: {restart_count})")
                    else:
                        print("❌ Failed to restart application")
                        break
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped by user")
    
    def cleanup(self):
        """Clean up old logs and temporary files"""
        print("🧹 Cleaning up...")
        
        # Clean old log files (keep last 10)
        if self.log_file.exists():
            # This is a simple cleanup - in production you might want more sophisticated log rotation
            pass
        
        # Clean Python cache
        for root, dirs, files in os.walk(self.app_dir):
            for dir_name in dirs:
                if dir_name == "__pycache__":
                    import shutil
                    shutil.rmtree(os.path.join(root, dir_name), ignore_errors=True)
        
        print("✅ Cleanup completed")

def main():
    manager = MultiUserAppManager()
    
    if len(sys.argv) < 2:
        print("King's Choice Management Multi-User System")
        print("Usage: python start_multi_user.py [command]")
        print("\nCommands:")
        print("  start     - Start the application in background")
        print("  start-fg  - Start the application in foreground")
        print("  stop      - Stop the application")
        print("  restart   - Restart the application")
        print("  status    - Show application status")
        print("  logs [N]  - Show last N lines of logs (default: 50)")
        print("  monitor   - Monitor and auto-restart application")
        print("  cleanup   - Clean up old files")
        print("  install   - Install dependencies only")
        print("  setup     - Setup database only")
        return
    
    command = sys.argv[1]
    
    if command == "start":
        manager.start_app(background=True)
    elif command == "start-fg":
        manager.start_app(background=False)
    elif command == "stop":
        manager.stop_app()
    elif command == "restart":
        manager.restart_app()
    elif command == "status":
        manager.status()
    elif command == "logs":
        lines = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        manager.logs(lines)
    elif command == "monitor":
        manager.monitor()
    elif command == "cleanup":
        manager.cleanup()
    elif command == "install":
        manager.install_dependencies()
    elif command == "setup":
        manager.setup_database()
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()