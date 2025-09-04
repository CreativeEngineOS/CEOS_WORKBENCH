# CEOS Workbench - Utilities Module
# Version: 1.1.0
# Date: 2025-09-01
# Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.
# 
# Purpose:
# A collection of shared helper functions used by various backend actors to
# perform common tasks, such as finding document paths and retrieving documents
# by their status.

import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_FOLDER = os.path.join(ROOT_DIR, '_ARCHIVE')

def find_doc_path(doc_id):
    """
    Finds the full path to a document's folder using its ID.
    This is now the single source of truth for locating documents.
    """
    year = doc_id.split('-')[0]
    year_folder = os.path.join(ARCHIVE_FOLDER, year)
    
    if not os.path.exists(year_folder):
        return None
    
    # The folder name must start with the ID followed by an underscore
    # to differentiate between '2025-001' and '2025-0011'.
    for folder_name in os.listdir(year_folder):
        if folder_name.startswith(doc_id + '_'):
            return os.path.join(year_folder, folder_name)
            
    return None

def get_all_doc_ids_by_status(status):
    """
    Returns a list of all document IDs that have a specific status.
    This is used to find all documents with a status of '_VOID'.
    """
    matching_ids = []

    for year_folder in os.listdir(ARCHIVE_FOLDER):
        year_path = os.path.join(ARCHIVE_FOLDER, year_folder)
        if not os.path.isdir(year_path) or year_folder.startswith('.'):
            continue

        for doc_folder in os.listdir(year_path):
            doc_path = os.path.join(year_path, doc_folder)
            json_path = os.path.join(doc_path, 'archive.json')

            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('status') == status:
                        matching_ids.append(data.get('id'))
    return matching_ids