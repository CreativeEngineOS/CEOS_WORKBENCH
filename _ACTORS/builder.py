# CEOS Workbench - Builder Actor
# Version: 1.1.0
# Date: 2025-09-01
# Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.
# 
# Purpose:
# This actor scans the entire _ARCHIVE directory and compiles all individual
# archive.json files into a single master database file (_APP/archive_db.json)
# that is served to the frontend. It also ensures file sizes and modification
# dates are kept up-to-date.

import os
import json
from datetime import datetime

# Define absolute paths from this file's location
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_FOLDER = os.path.join(ROOT_DIR, '_ARCHIVE')
DB_FILE_PATH = os.path.join(ROOT_DIR, '_APP/archive_db.json')

def run_builder():
    log = ["Builder dispatched."]
    master_list = []
    if not os.path.exists(ARCHIVE_FOLDER):
        log.append("Archive folder not found.")
        return "\n".join(log)

    for year in sorted(os.listdir(ARCHIVE_FOLDER), reverse=True):
        year_path = os.path.join(ARCHIVE_FOLDER, year)
        if os.path.isdir(year_path):
            for doc_folder in sorted(os.listdir(year_path)):
                doc_path = os.path.join(year_path, doc_folder)
                json_path = os.path.join(doc_path, 'archive.json')
                if os.path.exists(json_path):
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Update modification date and file sizes
                        data['dateModified'] = datetime.fromtimestamp(os.path.getmtime(json_path)).strftime('%Y-%m-%d %H:%M:%S')
                        for version in data['files']:
                            file_path = os.path.join(doc_path, data['files'][version]['name'])
                            if os.path.exists(file_path):
                                data['files'][version]['size'] = os.path.getsize(file_path)
                        
                        master_list.append(data)
                        
                        # Save the updated data back to the individual archive.json
                        with open(json_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2)
                            
                    except Exception as e:
                        log.append(f" > ERROR processing {json_path}: {e}")
    
    # Sort the final list by ID descending before saving
    master_list.sort(key=lambda x: x.get('id', ''), reverse=True)
    
    with open(DB_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(master_list, f, indent=2)
    
    log.append(f"Database rebuilt with {len(master_list)} entries.")
    return "\n".join(log)