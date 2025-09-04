# CEOS Workbench - Searcher Actor
# Version: 1.3.0
# Date: 2025-08-31
# Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.
# 
# Purpose:
# This actor powers the universal search functionality. It accepts a query string
# and returns a list of document IDs that match the query in either the title,
# tags, or the full text content of any of its Markdown files.


import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVE_FOLDER = os.path.join(ROOT_DIR, '_ARCHIVE')

def run_search(query):
    if not query:
        return []

    matching_ids = set()
    query = query.lower()

    for year_folder in os.listdir(ARCHIVE_FOLDER):
        year_path = os.path.join(ARCHIVE_FOLDER, year_folder)
        if not os.path.isdir(year_path) or year_folder.startswith('.'):
            continue
        
        for doc_folder in os.listdir(year_path):
            doc_path = os.path.join(year_path, doc_folder)
            if not os.path.isdir(doc_path) or doc_folder.startswith('.'):
                continue
            
            doc_id = doc_folder.split('_')[0]
            
            try:
                # 1. Search metadata (title and tags)
                json_path = os.path.join(doc_path, 'archive.json')
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                        if query in meta.get('title', '').lower():
                            matching_ids.add(doc_id)
                        if any(query in tag.lower() for tag in meta.get('tags', [])):
                            matching_ids.add(doc_id)

                # 2. Search content of all .md files
                for file in os.listdir(doc_path):
                    if file.endswith('.md'):
                        file_path = os.path.join(doc_path, file)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            if query in f.read().lower():
                                matching_ids.add(doc_id)
            except Exception as e:
                print(f"Error searching in {doc_path}: {e}")
                continue
    
    return sorted(list(matching_ids))