# CEOS Workbench - Librarian Actor
# Version: 1.2.0
# Date: 2025-09-01
# Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.
# 
# Purpose:
# This actor handles all read and write operations for an individual document's
# metadata (the archive.json file). It is the sole component responsible for
# getting and saving data like title, tags, synopsis, and editor notes.

import os
import json
from datetime import datetime
from .utils import find_doc_path # Use the shared utility

def get_metadata(doc_id):
    """Reads and returns the metadata from a document's archive.json file."""
    doc_path = find_doc_path(doc_id)
    if not doc_path:
        return None, f"Document with ID '{doc_id}' not found in archive."
    
    json_path = os.path.join(doc_path, 'archive.json')
    if not os.path.exists(json_path):
        return None, "Metadata file (archive.json) not found."
        
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, None
    except Exception as e:
        return None, f"Error reading metadata: {str(e)}"

def save_metadata(doc_id, new_data):
    """Saves updated metadata to a document's archive.json file."""
    doc_path = find_doc_path(doc_id)
    if not doc_path:
        return None, "Document not found."

    json_path = os.path.join(doc_path, 'archive.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data.update(new_data)
        data['dateModified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        return data, None
    except Exception as e:
        return None, f"Error saving metadata: {str(e)}"

def add_note(doc_id, note_data):
    """Adds a new editor note to a document's archive.json file."""
    doc_path = find_doc_path(doc_id)
    if not doc_path:
        return None, "Document not found."

    json_path = os.path.join(doc_path, 'archive.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'editorNotes' not in data or not isinstance(data['editorNotes'], list):
            data['editorNotes'] = []
            
        data['editorNotes'].append(note_data)
        data['dateModified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        return data, None
    except Exception as e:
        return None, f"Error adding note: {str(e)}"