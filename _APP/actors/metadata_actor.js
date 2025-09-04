/*
    CEOS Workbench - Metadata Actor
    Version: 1.1.2
    Date: 2025-09-02
    Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.

    Purpose:
    This actor controls the behavior of the right-hand "Information" panel.
    It is responsible for fetching, rendering, and saving a document's
    metadata, such as its title, tags, and editor notes.
*/
let elements = {};
let currentItem = null;
let isEditing = false;

async function _render(isEditing = false) {
    if (!currentItem) return;
    const response = await fetch(`/api/metadata/${currentItem.id}`);
    const result = await response.json();
    if (result.status !== 'success') {
        if (elements.infoContent) elements.infoContent.innerHTML = `<p class="text-red-500">Could not load metadata.</p>`;
        return;
    }
    const data = result.data;
    currentItem = data;

    const tagsHtml = (data.tags && data.tags.length > 0)
        ? data.tags.map(tag => `<span class="tag-badge">${tag}</span>`).join('')
        : '<p class="text-gray-500 italic">No tags</p>';
    let notesHtml = '';
    if (data.editorNotes && data.editorNotes.length > 0) {
        notesHtml = data.editorNotes.map(note =>
            `<li class="p-2 bg-gray-900 rounded-md text-xs">
                <strong class="text-gray-400">"${note.selection}"</strong>
                <p class="italic text-gray-500 ml-2">- ${note.comment}</p>
            </li>`
        ).join('');
    } else {
        notesHtml = `<li class="text-xs text-gray-500 italic">No notes for this version.</li>`;
    }
    if (isEditing) {
        if (elements.infoContent) {
            elements.infoContent.innerHTML = `
                <div class="info-item">
                    <label>Title</label>
                    <input type="text" id="info-edit-title" class="form-input w-full p-1 rounded text-sm" value="${data.title || ''}">
                </div>
                <div class="info-item">
                    <label>Tags (comma-separated)</label>
                    <input type="text" id="info-edit-tags" class="form-input w-full p-1 rounded text-sm" value="${(data.tags || []).join(', ')}">
                </div>
                <div class="info-item">
                    <label>Synopsis</label>
                    <textarea id="info-edit-synopsis" class="form-input w-full p-1 rounded text-sm" rows="4">${data.synopsis || ''}</textarea>
                </div>
            `;
        }
    } else {
        if (elements.infoContent) {
            elements.infoContent.innerHTML = `
                <div class="info-item"><label>Title</label><p>${data.title}</p></div>
                <div class="info-item"><label>Status</label><p>${data.status}</p></div>
                <div class="info-item"><label>Tags</label><div class="flex flex-wrap gap-2 mt-1">${tagsHtml}</div></div>
                <div class="info-item"><label>ID</label><p>${data.id}</p></div>
                <div class="info-item"><label>Last Modified</label><p>${data.dateModified}</p></div>
                <div class="pt-2"><h3 class="text-md font-semibold mb-2">Editor Notes</h3><ul class="space-y-2">${notesHtml}</ul></div>
            `;
        }
    }
    if (elements.infoEditBtn) elements.infoEditBtn.style.display = isEditing ? 'none' : 'flex';
    if (elements.infoSaveBtn) elements.infoSaveBtn.style.display = isEditing ? 'flex' : 'none';
}

async function _handleSave() {
    const tagsValue = document.getElementById('info-edit-tags')?.value;
    if (!tagsValue) {
        alert("Tags field is missing.");
        return;
    }
    const updatedData = {
        title: document.getElementById('info-edit-title')?.value,
        tags: tagsValue.split(',').map(tag => tag.trim()).filter(tag => tag),
        synopsis: document.getElementById('info-edit-synopsis')?.value,
    };
    const response = await fetch(`/api/metadata/${currentItem.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData)
    });
    if (response.ok) {
        currentItem = { ...currentItem, ...updatedData };
        await _render(false);
        document.dispatchEvent(new CustomEvent('metadataUpdated'));
    } else {
        alert('Failed to save metadata.');
    }
}

export function init(elementRefs) {
    elements = elementRefs;
    if (elements.infoEditBtn) elements.infoEditBtn.addEventListener('click', () => _render(true));
    if (elements.infoSaveBtn) elements.infoSaveBtn.addEventListener('click', _handleSave);
}

export async function renderInfoColumn(selectedItem) {
    currentItem = selectedItem;
    await _render(false);
}