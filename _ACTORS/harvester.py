# CEOS Workbench - Harvester Actor
# Version: 1.1.0
# Date: 2025-09-01
# Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.
# 
# Purpose:
# This actor is responsible for the initial ingestion of new files. It scans the
# designated ingest folder, creates a structured and versioned folder for each
# new document in the archive, converts content to Markdown, and generates the
# initial metadata file.

import os
import json
import shutil
import re
from datetime import datetime
from striprtf.striprtf import rtf_to_text
from .settings_actor import get_ingest_folder_path # <-- IMPORT

# Define absolute paths from this file's location
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# INGEST_FOLDER is now determined dynamically
ARCHIVE_FOLDER = os.path.join(ROOT_DIR, '_ARCHIVE')
PROCESSED_FOLDER = os.path.join(ROOT_DIR, '_PROCESSED')
CONFIG_LUT_PATH = os.path.join(ROOT_DIR, '_LUTS/_LUT_SYSTEM_CONFIG.json')

def get_next_id(year_folder):
    if not os.path.exists(year_folder): return "001"
    existing_ids = [int(d.split('_')[0].split('-')[1]) for d in os.listdir(year_folder) if d.startswith(str(datetime.now().year)) and '-' in d]
    if not existing_ids: return "001"
    return str(max(existing_ids) + 1).zfill(3)

def sanitize_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ', '_', '-')).rstrip()

def load_config():
    try:
        with open(CONFIG_LUT_PATH, 'r', encoding='utf-8') as f: config_data = json.load(f)
        return {item['key']: item['value'] for item in config_data.get('config', [])}
    except Exception: return {"author": "Default Author", "copyright": "Default Copyright"}

def extract_rtf_metadata(rtf_content):
    metadata = {}
    author_match = re.search(r'\{\\author\s+([^}]+)\}', rtf_content);
    if author_match: metadata['author'] = author_match.group(1).strip()
    copyright_match = re.search(r'\{\*\\copyright\s+([^}]+)\}', rtf_content)
    if copyright_match: metadata['copyright'] = copyright_match.group(1).strip()
    return metadata

def _create_archive_structure(filename, content):
    config = load_config()
    now = datetime.now()
    year_str = str(now.year)
    year_folder = os.path.join(ARCHIVE_FOLDER, year_str)
    if not os.path.exists(year_folder): os.makedirs(year_folder)

    new_id = f"{year_str}-{get_next_id(year_folder)}"
    base_name = os.path.splitext(filename)[0]
    sanitized_title = sanitize_filename(base_name)
    doc_folder_name = f"{new_id}_{sanitized_title}"
    doc_folder_path = os.path.join(year_folder, doc_folder_name)
    os.makedirs(doc_folder_path)

    # Clean content before writing
    cleaned_content = rtf_to_text(content) if content.strip().startswith('{\\rtf') else content
    with open(os.path.join(doc_folder_path, 'raw.md'), 'w', encoding='utf-8') as f: f.write(cleaned_content)
    
    # Create empty files for other versions
    for version in ['draft.md', 'edited.md', 'published.md']:
        open(os.path.join(doc_folder_path, version), 'w').close()
    
    file_type = "Rich Text" if filename.lower().endswith('.rtf') else "Text"
    metadata = extract_rtf_metadata(content) if file_type == "Rich Text" else {}

    json_template = {
        "id": new_id,
        "title": base_name,
        "folderName": doc_folder_name,
        "author": metadata.get('author', config.get('author')),
        "copyright": metadata.get('copyright', config.get('copyright')),
        "status": "Raw",
        "type": file_type,
        "dateCreated": now.strftime("%Y-%m-%d"),
        "dateModified": now.strftime("%Y-%m-%d %H:%M:%S"),
        "location": "",
        "language": "English",
        "summary": "",
        "concepts": [],
        "voiceTone": { "keywords": [], "summary": "" },
        "files": {
            "raw": {"name": "raw.md", "size": len(cleaned_content.encode('utf-8'))},
            "draft": {"name": "draft.md", "size": 0},
            "edited": {"name": "edited.md", "size": 0},
            "published": {"name": "published.md", "size": 0}
        }
    }
    
    with open(os.path.join(doc_folder_path, 'archive.json'), 'w', encoding='utf-8') as f:
        json.dump(json_template, f, indent=2)

def run_harvester():
    log = ["Harvester dispatched."]
    ingest_folder = get_ingest_folder_path() # <-- DYNAMIC PATH
    log.append(f"Scanning ingest folder: {ingest_folder}")

    if not os.path.exists(ingest_folder) or not os.listdir(ingest_folder):
        log.append("No new files to ingest.")
        return "\n".join(log)
    
    if not os.path.exists(PROCESSED_FOLDER): os.makedirs(PROCESSED_FOLDER)

    processed_files = []
    for filename in os.listdir(ingest_folder):
        source_path = os.path.join(ingest_folder, filename)
        if os.path.isfile(source_path):
            log.append(f" > Processing: {filename}")
            try:
                with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                _create_archive_structure(filename, content)
                
                shutil.move(source_path, os.path.join(PROCESSED_FOLDER, filename))
                processed_files.append(filename)
                log.append(f"  > Success for {filename}.")
            except Exception as e:
                log.append(f"  > ERROR: {e}")
    
    return f"Harvested {len(processed_files)} file(s)."