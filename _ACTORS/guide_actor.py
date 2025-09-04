# CEOS Workbench - Guide Actor
# Version: 1.1.0 (dev)
# Date: 2025-09-02
# Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.
# Purpose: Serves content for the Visual Guide feature. Includes debugging prints.

import os
import json
from flask import send_from_directory

# Define absolute paths from this file's location
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VISUALS_FOLDER = os.path.join(ROOT_DIR, '_APP', 'assets', 'visuals')
GUIDES_FOLDER = os.path.join(ROOT_DIR, '_APP', 'guides')

def serve_guide_visual(visual_id):
    """Serves a requested SVG file from the assets folder."""
    
    # --- DEBUGGING LINE ---
    # This will print the exact path the server is checking to your terminal.
    print(f"DEBUG: Attempting to serve visual from path: {os.path.join(VISUALS_FOLDER, visual_id)}")
    # --- END DEBUGGING ---
    
    if os.path.exists(os.path.join(VISUALS_FOLDER, visual_id)):
        return send_from_directory(VISUALS_FOLDER, visual_id)
    return None

def get_guide_step(guide_id, step_number):
    """Reads and returns the markdown content for a specific guide step."""
    file_name = f"{guide_id}_step_{step_number}.md"
    file_path = os.path.join(GUIDES_FOLDER, guide_id, file_name)

    # --- DEBUGGING LINE ---
    print(f"DEBUG: Attempting to read guide step from path: {file_path}")
    # --- END DEBUGGING ---
    
    if not os.path.exists(file_path):
        return {"content": f"## Step Not Found\n\nCould not find content for step {step_number} of the '{guide_id}' guide."}, None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content}, None
    except Exception as e:
        return None, f"Error reading guide step {file_path}: {str(e)}"

