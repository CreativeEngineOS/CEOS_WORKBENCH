# CEOS Workbench - Saver Actor
# Version: 1.0.0
# Date: 2025-09-01
# Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.
# 
# Purpose:
# This actor has the single responsibility of saving new text content from the
# front-end editor into the correct file (draft.md or edited.md) within the
# document's archive folder.

import os
import json
from datetime import datetime
from .utils import find_doc_path # Use the shared utility

def save_changes(doc_id, version, content):
    """Overwrites a version file with new content and updates metadata."""
    doc_path = find_doc_path(doc_id)
    if not doc_path:
        return None, "Document not found."
    if version not in ['draft', 'edited']:
        return None, f"Saving is not permitted for the '{version}' stage."

    version_path = os.path.join(doc_path, f"{version}.md")
    json_path = os.path.join(doc_path, 'archive.json')

    try:
        with open(version_path, 'w', encoding='utf-8') as f:
            f.write(content)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['dateModified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['files'][version]['size'] = os.path.getsize(version_path)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return data, None
    except Exception as e:
        return None, f"Error saving changes: {str(e)}"