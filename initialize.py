# app/initialize.py
import sys
import os
from pathlib import Path

def setup_paths():
    # Get the absolute path of the app directory
    app_dir = Path(__file__).parent.absolute()
    
    # Get the project root directory (parent of app directory)
    project_root = app_dir.parent
    
    # Add paths to sys.path if they're not already there
    paths_to_add = [
        str(project_root),  # Add project root
        str(app_dir),       # Add app directory
        str(app_dir / 'agents'),    # Add agents directory
        str(app_dir / 'utils'),     # Add utils directory
        str(app_dir / 'workflow'),  # Add workflow directory
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    # Set environment variables if needed
    os.environ['PROJECT_ROOT'] = str(project_root)
    os.environ['APP_ROOT'] = str(app_dir)





    

