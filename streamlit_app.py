#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path

def run_setup():
    """Run the setup script before starting the app."""
    try:
        # Make sure setup.sh is executable
        setup_script = Path(__file__).parent / 'setup.sh'
        if not setup_script.exists():
            print(f"Error: {setup_script} not found!")
            return False
        
        # Make the script executable
        setup_script.chmod(0o755)
        
        # Run the setup script
        print("Running setup script...")
        result = subprocess.run(
            [str(setup_script)],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=sys.stdout,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Setup script failed with error:\n{result.stderr}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error during setup: {str(e)}")
        return False

if __name__ == "__main__":
    # Run the setup script
    if not run_setup():
        print("Warning: Setup script encountered issues. The app may not work correctly.")
    
    # Import and run the main app
    try:
        from app import main
        main()
    except Exception as e:
        print(f"Error starting the application: {str(e)}")
        raise
