# CEOS Workbench - Promoter Actor
# Version: 1.1.0
# Date: 2025-09-01
# Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.
# 
# Purpose:
# This actor manages the document's workflow progression. It contains the logic
# for copying content between versions (e.g., from raw to draft) and updating
# the document's status in its metadata file at each stage.


import os
import json
import shutil
from datetime import datetime
from .utils import find_doc_path # Use the shared utility

def create_draft(doc_id):
    """Copies content from raw.md to draft.md and updates metadata."""
    doc_path = find_doc_path(doc_id)
    if not doc_path:
        return None, "Document not found."

    raw_path = os.path.join(doc_path, 'raw.md')
    draft_path = os.path.join(doc_path, 'draft.md')
    json_path = os.path.join(doc_path, 'archive.json')

    try:
        shutil.copyfile(raw_path, draft_path)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['status'] = 'Draft'
        data['dateModified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['files']['draft']['size'] = os.path.getsize(draft_path)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return data, None
    except Exception as e:
        return None, f"Error creating draft: {str(e)}"

def promote_to_edited(doc_id):
    """Copies content from draft.md to edited.md and updates metadata."""
    doc_path = find_doc_path(doc_id)
    if not doc_path:
        return None, "Document not found."

    draft_path = os.path.join(doc_path, 'draft.md')
    edited_path = os.path.join(doc_path, 'edited.md')
    json_path = os.path.join(doc_path, 'archive.json')

    if not os.path.exists(draft_path) or os.path.getsize(draft_path) == 0:
        return None, "Cannot promote. The 'draft' version is empty."

    try:
        shutil.copyfile(draft_path, edited_path)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['status'] = 'Edited'
        data['dateModified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['files']['edited']['size'] = os.path.getsize(edited_path)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return data, None
    except Exception as e:
        return None, f"Error promoting to edited: {str(e)}"

def approve_for_publish(doc_id):
    """Copies content from edited.md to published.md and updates metadata."""
    doc_path = find_doc_path(doc_id)
    if not doc_path:
        return None, "Document not found."

    edited_path = os.path.join(doc_path, 'edited.md')
    published_path = os.path.join(doc_path, 'published.md')
    json_path = os.path.join(doc_path, 'archive.json')

    if not os.path.exists(edited_path) or os.path.getsize(edited_path) == 0:
        return None, "Cannot publish. The 'edited' version is empty."

    try:
        shutil.copyfile(edited_path, published_path)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['status'] = 'Published'
        data['dateModified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['files']['published']['size'] = os.path.getsize(published_path)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return data, None
    except Exception as e:
        return None, f"Error publishing document: {str(e)}"

# --- NEW ACTOR FUNCTION ---
def void_document(doc_id):
    """Changes a document's status to _VOID, effectively removing it from the UI."""
    doc_path = find_doc_path(doc_id)
    if not doc_path:
        return None, "Document not found."
    
    json_path = os.path.join(doc_path, 'archive.json')

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['status'] = '_VOID'
        data['dateModified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        return data, None
    except Exception as e:
        return None, f"Error voiding document: {str(e)}"