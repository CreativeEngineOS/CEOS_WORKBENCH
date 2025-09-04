/*
    CEOS Workbench - Highlight Actor
    Version: 1.1.1
    Date: 2025-09-01
    Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.

    Purpose:
    This actor manages the right-click context menu within the text editor.
    It captures highlighted text and provides the "Add to Style Guide" and
    "Add Note" functionalities.
*/
let _popupElement = null;
let _editorElement = null;
let _statusElement = null;
let _selectedText = '';
let _getCurrentItem = null;

function _createPopup() {
    const popupHtml = `
        <div id="highlight-popup" class="absolute card p-2 rounded-md shadow-lg hidden z-50 flex flex-col space-y-1">
            <button id="add-to-styleguide-btn" class="btn btn-primary text-xs w-full text-left">Add to Style Guide</button>
            <button id="add-note-btn" class="btn btn-secondary text-xs w-full text-left">Add Note...</button>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', popupHtml);
    _popupElement = document.getElementById('highlight-popup');
    _popupElement.querySelector('#add-to-styleguide-btn').addEventListener('click', _handleAddToGuide);
    _popupElement.querySelector('#add-note-btn').addEventListener('click', _handleAddNote);
}

function _handleContextMenu(event) {
    event.preventDefault();
    setTimeout(() => {
        const selection = window.getSelection();
        _selectedText = selection.toString().trim();
        if (_selectedText.length > 0) {
            _popupElement.style.left = `${event.pageX}px`;
            _popupElement.style.top = `${event.pageY}px`;
            _popupElement.classList.remove('hidden');
        } else {
            _popupElement.classList.add('hidden');
        }
    }, 10);
}

async function _handleAddToGuide() {
    if (!_selectedText) return;
    _popupElement.classList.add('hidden');
    _statusElement.textContent = `Adding "${_selectedText}" to Style Guide...`;
    const response = await fetch('/api/styleguide/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phrase: _selectedText })
    });
    _statusElement.textContent = response.ok ? `"${_selectedText}" was added successfully.` : `Error: Could not add phrase.`;
    window.getSelection().removeAllRanges();
}

async function _handleAddNote() {
    if (!_selectedText) return;
    _popupElement.classList.add('hidden');
    
    const comment = prompt(`Enter a note for the selection:\n\n"${_selectedText}"`);
    if (!comment || comment.trim() === '') return;

    const currentItem = _getCurrentItem();
    if (!currentItem) {
        _statusElement.textContent = 'Error: No document selected.';
        return;
    }

    _statusElement.textContent = 'Adding note...';
    const response = await fetch(`/api/notes/add/${currentItem.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selection: _selectedText, comment: comment.trim() })
    });

    if (response.ok) {
        _statusElement.textContent = 'Note added successfully.';
        document.dispatchEvent(new CustomEvent('metadataUpdated'));
    } else {
        _statusElement.textContent = 'Error: Could not add note.';
    }
    window.getSelection().removeAllRanges();
}

export function init(editorEl, statusEl, getCurrentItemFn) {
    if (!editorEl) {
        console.warn('HighlightActor: Editor element not found. Context menu will be disabled.');
        return;
    }
    _editorElement = editorEl;
    _statusElement = statusEl;
    _getCurrentItem = getCurrentItemFn; 
    _createPopup();
    _editorElement.addEventListener('contextmenu', _handleContextMenu);
    document.addEventListener('click', (event) => {
        if (_popupElement && !_popupElement.contains(event.target)) {
            _popupElement.classList.add('hidden');
        }
    });
}