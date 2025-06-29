import subprocess
import sys
import os

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Create a single executable file
        "--windowed",  # Don't show console window
        "--name=TimeTracker",  # Name of the executable
        "--icon=icon.ico",  # Icon file (if available)
        "time_tracker.py"
    ]
    
    # Remove icon parameter if icon file doesn't exist
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon=icon.ico")
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print(f"Executable created in: dist/TimeTracker.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Please install it first:")
        print("pip install pyinstaller")
        return False
    
    return True

if __name__ == "__main__":
    build_executable() 