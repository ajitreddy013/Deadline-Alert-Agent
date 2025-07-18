import subprocess
import platform

def send_desktop_notification(title: str, message: str):
    """Send desktop notification using platform-specific method"""
    try:
        if platform.system() == 'Darwin':  # macOS
            # Use macOS native notification system
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(['osascript', '-e', script], check=True)
        elif platform.system() == 'Linux':
            # Use notify-send on Linux
            subprocess.run(['notify-send', title, message], check=True)
        elif platform.system() == 'Windows':
            # Use powershell on Windows
            script = f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show("{message}", "{title}")'
            subprocess.run(['powershell', '-Command', script], check=True)
        else:
            print(f"Desktop notification: {title} - {message}")
    except Exception as e:
        print(f"Failed to send notification: {e}")
        print(f"Notification: {title} - {message}")
