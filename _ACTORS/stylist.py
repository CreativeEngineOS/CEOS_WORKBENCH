# CEOS Workbench - Stylist Actor
# Version: 1.1.0
# Date: 2025-09-01
# Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.
# 
# Purpose:
# This actor manages the global Style Guide (_LUTS/_LUT_STYLE_GUIDE.json).
# It now handles fetching, adding, and removing phrases from the guide.

import os
import json

# Define absolute paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE_GUIDE_PATH = os.path.join(ROOT_DIR, '_LUTS/_LUT_STYLE_GUIDE.json')

def get_style_guide():
    """Reads and returns the entire style guide data."""
    try:
        with open(STYLE_GUIDE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, None
    except Exception as e:
        return None, f"Error reading style guide: {str(e)}"

def add_to_style_guide(phrase):
    """Adds a new phrase to the style guide, avoiding duplicates."""
    try:
        data, error = get_style_guide()
        if error: return None, error
        
        if phrase and phrase not in data.get('phrases', []):
            data.setdefault('phrases', []).append(phrase)
            data['phrases'].sort()
        
        with open(STYLE_GUIDE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return data, None
    except Exception as e:
        return None, f"Error updating style guide: {str(e)}"

def remove_from_style_guide(phrase):
    """Removes a phrase from the style guide."""
    try:
        data, error = get_style_guide()
        if error: return None, error
        
        if phrase and phrase in data.get('phrases', []):
            data['phrases'].remove(phrase)
        
        with open(STYLE_GUIDE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        return data, None
    except Exception as e:
        return None, f"Error updating style guide: {str(e)}"
    
def edit_style_guide_phrase(old_phrase, new_phrase):
    """Edits an existing phrase in the style guide."""
    try:
        data, error = get_style_guide()
        if error: return None, error

        if old_phrase and new_phrase and old_phrase in data.get('phrases', []):
            # Find the index of the old phrase and replace it
            index = data['phrases'].index(old_phrase)
            data['phrases'][index] = new_phrase
            data['phrases'].sort() # Keep the list sorted
        else:
            return None, "Old phrase not found or new phrase not provided."

        with open(STYLE_GUIDE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        return data, None
    except Exception as e:
        return None, f"Error updating style guide: {str(e)}"