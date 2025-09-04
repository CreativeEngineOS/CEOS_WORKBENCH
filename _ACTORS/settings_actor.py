# CEOS Workbench - Settings Actor
# Version: 1.3.0
# Date: 2025-09-02
# Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.
#
# Purpose:
# Manages all backend administrative and configuration tasks, including reading/writing
# user settings, managing the ingest folder path, and handling the permanent
# deletion of documents from the archive.

import os
import json
import shutil
from .utils import find_doc_path, get_all_doc_ids_by_status

# Define absolute paths from this file's location
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_CONFIG_PATH = os.path.join(ROOT_DIR, '_LUTS/_LUT_USER_CONFIG.json')
ARCHIVE_FOLDER = os.path.join(ROOT_DIR, '_ARCHIVE')

def get_settings():
    """Reads and returns all settings from the user configuration file."""
    if not os.path.exists(USER_CONFIG_PATH):
        # Create a default config if it doesn't exist
        default_settings = {
            "description": "User-specific configuration and settings.",
            "settings": {
                "ingest_folder_path": "_INGEST",
                "void_folder_path": "_VOID",
                "purge_confirmation": True,
                "theme": "theme-default",
                "spacing": "spacing-default",
                "textSize": "text-medium"
            }
        }
        with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_settings, f, indent=2)
        return default_settings, None
    try:
        with open(USER_CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data, None
    except Exception as e:
        return None, f"Error reading user settings: {str(e)}"

def save_settings(new_settings):
    """Saves updated settings to the user configuration file."""
    try:
        # First, get the full existing configuration data
        data, error = get_settings()
        if error: return None, error
        
        #
        # --- THIS IS THE FIX ---
        # Instead of just updating, we will replace the settings
        # to ensure new keys like 'tooltips_enabled' are added correctly.
        #
        data['settings'] = new_settings
        
        with open(USER_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        return data, None
    except Exception as e:
        return None, f"Error saving settings: {str(e)}"

def set_ingest_folder(path_str):
    """Validates and saves a new path for the ingest folder."""
    if not os.path.isdir(path_str):
        return None, f"Error: The provided path '{path_str}' is not a valid directory."
    
    return save_settings({"ingest_folder_path": path_str})

def get_ingest_folder_path():
    """Reads the config and returns the absolute path to the ingest folder."""
    settings, error = get_settings()
    if error:
        print(f"Warning: Could not read user settings. Defaulting to '_INGEST'. Error: {error}")
        return os.path.join(ROOT_DIR, '_INGEST')
    
    relative_path = settings.get('settings', {}).get('ingest_folder_path', '_INGEST')
    # If the path is already absolute, use it directly. Otherwise, join with ROOT_DIR.
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(ROOT_DIR, relative_path)
    
def purge_voided_documents():
    """
    Permanently deletes all document folders with the status '_VOID'
    and rebuilds the main database.
    """
    void_ids = get_all_doc_ids_by_status('_VOID')
    log = []
    
    if not void_ids:
        return "No voided documents to purge.", None
        
    for doc_id in void_ids:
        doc_path = find_doc_path(doc_id)
        if doc_path:
            try:
                shutil.rmtree(doc_path)
                log.append(f" - Successfully deleted folder for document {doc_id}.")
            except Exception as e:
                log.append(f" - ERROR deleting folder for document {doc_id}: {e}")
    
    return "\n".join(log), None

def delete_document_from_archive(doc_id):
    """
    Permanently deletes a single document's folder from the archive.
    """
    doc_path = find_doc_path(doc_id)
    if not doc_path:
        return None, "Document not found."

    try:
        shutil.rmtree(doc_path)
        return f"Document {doc_id} and its files have been permanently deleted.", None
    except Exception as e:
        return None, f"Error deleting document {doc_id}: {str(e)}"