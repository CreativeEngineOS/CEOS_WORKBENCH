/*
    CEOS Workbench - Settings Actor
    Version: 1.0.1 (Hotfix)
    Date: 2025-09-03
    Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.

    Purpose:
    Manages the functionality of the main settings panel, including its
    various tabs like Appearance, Style Guide, and File Manager.
*/

// --- Module-level State ---
let elements = {};
let archiveData = [];
// A function passed from main_actor to update the main panel state
let updateMainPanelStateFn = () => {}; 
// A function passed from main_actor to reload archive data
let loadArchiveFn = () => {}; 


/**
 * Toggles the visibility of the settings panel.
 * Calls a function from the main actor to update the overall UI state.
 */
export function toggle() {
    const isVisible = elements.settingsPanel?.style.display === 'flex';
    document.body.classList.toggle('settings-active', !isVisible);

    if (!isVisible) {
        elements.settingsTabs?.querySelector('[data-tab="appearance"]')?.click();
    }
    
    const selectedItem = window.mainActor.getSelectedItem();
    updateMainPanelStateFn(isVisible ? (selectedItem ? 'viewer' : 'welcome') : 'settings');
}

// ===================================================================================
//
//  SETTINGS PANEL RENDERERS AND HANDLERS
//
// ===================================================================================


async function _renderAppearanceSettingsView() {
    const container = document.getElementById('appearance');
    if (!container) return;
    try {
        const response = await fetch('/api/settings');
        const result = await response.json();
        if (result.status === 'success') {
            const settings = result.data.settings;
            container.querySelector(`input[name="theme"][value="${settings.theme}"]`)?.setAttribute('checked', 'true');
            container.querySelector(`input[name="transparency"][value="${settings.transparency}"]`)?.setAttribute('checked', 'true');
            container.querySelector(`input[name="textSize"][value="${settings.textSize}"]`)?.setAttribute('checked', 'true');
            container.querySelector(`input[name="spacing"][value="${settings.spacing}"]`)?.setAttribute('checked', 'true');
        }
    } catch (error) {
        console.error('Error loading appearance settings:', error);
    }
}

function _previewAppearanceSettings() {
    const form = document.getElementById('appearance-settings-form');
    if (!form) return;
    const theme = form.elements['theme'].value;
    const transparency = form.elements['transparency'].value;
    const spacing = form.elements['spacing'].value;
    const textSize = form.elements['textSize'].value;
    const body = document.body;
    body.classList.remove('theme-dimmed', 'theme-light', 'spacing-compact', 'spacing-relaxed', 'spacing-spacious', 'text-small', 'text-large', 'transparency-flat', 'transparency-lightweight', 'transparency-default');
    if (theme && theme !== 'theme-default') body.classList.add(theme);
    if (spacing && spacing !== 'spacing-relaxed') body.classList.add(spacing);
    if (textSize && textSize !== 'text-medium') body.classList.add(textSize);
    if (transparency) body.classList.add(transparency);
}

async function _renderStyleGuideView() {
    const container = document.getElementById('styleguide');
    if (!container) return;
    container.innerHTML = `<div class="p-4 space-y-4"><div class="card mb-4"><h3 class="text-lg font-semibold mb-2">Add New Phrase</h3><div class="flex space-x-2"><input type="text" id="new-phrase-input" class="form-input w-full" placeholder="Enter new phrase..."><button id="add-phrase-btn" class="btn btn-primary">Add</button></div></div><div id="style-guide-list-container" class="space-y-2"></div></div>`;
    const listContainer = container.querySelector('#style-guide-list-container');
    try {
        const response = await fetch('/api/styleguide');
        const result = await response.json();
        if (result.status === 'success') {
            const phrases = result.data.phrases || [];
            listContainer.innerHTML = phrases.length === 0 ? `<p class="text-gray-500 text-sm p-4">No phrases.</p>` : `<ul class="space-y-2">` + phrases.map(p => `<li class="card p-2 flex justify-between items-center text-sm"><span>${p}</span><div class="flex items-center space-x-2"><button class="btn btn-secondary text-xs edit-phrase-btn" data-phrase="${p}">Edit</button><button class="btn btn-negative text-xs remove-phrase-btn" data-phrase="${p}">&times;</button></div></li>`).join('') + `</ul>`;
        } else { listContainer.innerHTML = `<p class="text-red-400 p-4">Error loading Style Guide.</p>`; }
    } catch (error) { listContainer.innerHTML = `<p class="text-red-400 p-4">Could not connect to server.</p>`; }
    container.querySelector('#add-phrase-btn')?.addEventListener('click', async () => { const phrase = container.querySelector('#new-phrase-input').value.trim(); if (phrase) { await fetch('/api/styleguide/add', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phrase }) }); _renderStyleGuideView(); } });
    container.querySelectorAll('.edit-phrase-btn').forEach(btn => btn.addEventListener('click', async (e) => { const oldPhrase = e.target.dataset.phrase; const newPhrase = prompt('Edit phrase:', oldPhrase); if (newPhrase && newPhrase.trim() !== oldPhrase) { await fetch('/api/styleguide/edit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ old_phrase: oldPhrase, new_phrase: newPhrase.trim() }) }); _renderStyleGuideView(); } }));
    container.querySelectorAll('.remove-phrase-btn').forEach(btn => btn.addEventListener('click', async (e) => { const phrase = e.target.dataset.phrase; if (confirm(`Remove "${phrase}"?`)) { await fetch('/api/styleguide/remove', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phrase }) }); _renderStyleGuideView(); } }));
}

/**
 * <<< FUNCTION MOVED FROM MAIN_ACTOR.JS >>>
 * Handles the prompt and API call to set the ingest folder path.
 */
async function _handleSetIngestFolder() {
    const response = await fetch('/api/settings');
    if (!response.ok) { alert("Could not load current settings."); return; }
    const currentSettings = await response.json();
    const currentPath = currentSettings.data.settings.ingest_folder_path;
    const newPath = prompt("Please enter the full, absolute path for the new ingest folder:", currentPath);
    if (!newPath || newPath === currentPath) return;
    const saveResponse = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ "ingest_folder_path": newPath })
    });
    const result = await saveResponse.json();
    if (result.status === 'success') {
        if (elements.statusMessage) elements.statusMessage.textContent = "Ingest folder updated successfully.";
        _renderSettingsView(); // Re-render to show the new path
    } else {
        const errorMessage = result.message || "An unknown error occurred.";
        if (elements.statusMessage) elements.statusMessage.textContent = `Error: ${errorMessage}`;
        alert(`Error: ${errorMessage}`);
    }
}


function _renderSettingsView() {
    if (elements.config) {
        elements.config.innerHTML = `<div class="p-4"><h3 class="text-lg font-semibold mb-2">Ingest Folder</h3><div class="card p-4 space-y-2"><p class="text-gray-400 text-sm">Current path: <code id="ingest-path" class="text-xs bg-gray-900 p-1 rounded">...</code></p><button id="set-ingest-folder-btn" class="btn btn-secondary w-full">Set Ingest Folder</button></div></div>`;
        document.getElementById('set-ingest-folder-btn')?.addEventListener('click', _handleSetIngestFolder);
        fetch('/api/settings').then(res => res.json()).then(result => { if(result.status === 'success') document.getElementById('ingest-path').textContent = result.data.settings.ingest_folder_path; });
    }
}

async function _handleDeleteFile(docId) {
    if (!confirm(`Are you sure you want to permanently delete document "${docId}"? This action cannot be undone.`)) return;
    if (elements.statusMessage) elements.statusMessage.textContent = `Deleting document ${docId}...`;
    const response = await fetch(`/api/settings/delete/${docId}`, { method: 'POST' });
    const result = await response.json();
    if (result.status === 'success') {
        if (elements.statusMessage) elements.statusMessage.textContent = 'Document deleted.';
        loadArchiveFn();
    } else {
        if (elements.statusMessage) elements.statusMessage.textContent = `Error: ${result.message}`;
    }
}

function _renderVoidedDocsList() {
    const container = document.getElementById('filemanager');
    if (!container) return;
    container.innerHTML = `<div class="p-4 space-y-4"><div class="flex justify-between items-center"><h3 class="text-lg font-semibold">Voided Documents</h3></div><div id="void-list-container" class="space-y-2"></div></div>`;
    const listContainer = container.querySelector('#void-list-container');
    const voidedDocs = archiveData.filter(item => item.status === '_VOID');
    if (voidedDocs.length === 0) { listContainer.innerHTML = `<p class="text-gray-500 text-sm p-4">No documents in The VOID.</p>`; } else { listContainer.innerHTML = voidedDocs.map(item => `<div class="p-3 card list-item"><div class="flex items-center justify-between"><span class="font-bold text-sm">${item.title}</span><button class="btn btn-negative text-xs delete-void-btn" data-doc-id="${item.id}">Delete</button></div></div>`).join(''); }
    listContainer.querySelectorAll('.delete-void-btn').forEach(btn => btn.addEventListener('click', (e) => { e.stopPropagation(); _handleDeleteFile(e.target.dataset.docId); }));
}

function _handleSettingsTabClick(e) {
    const tabButton = e.target.closest('.settings-tab-btn');
    if (!tabButton) return;
    elements.settingsTabs.querySelectorAll('.settings-tab-btn').forEach(t => t.classList.remove('active'));
    elements.settingsPanel.querySelectorAll('.guide-tab-panel').forEach(p => p.classList.remove('active'));
    tabButton.classList.add('active');
    const tabName = tabButton.dataset.tab;
    const contentEl = document.getElementById(tabName);
    if (contentEl) {
        contentEl.classList.add('active');
        switch (tabName) {
            case 'config': _renderSettingsView(); break;
            case 'filemanager': _renderVoidedDocsList(); break;
            case 'styleguide': _renderStyleGuideView(); break;
            case 'appearance': _renderAppearanceSettingsView(); break;
        }
    }
}

/**
 * Initializes the Settings Actor.
 * @param {object} elementRefs - A dictionary of DOM element references.
 * @param {Function} updateStateFn - A callback to update the main panel's state.
 * @param {Function} loadArchiveCallback - A callback to reload the archive data.
 */
export function init(elementRefs, updateStateFn, loadArchiveCallback) {
    elements = elementRefs;
    updateMainPanelStateFn = updateStateFn;
    loadArchiveFn = loadArchiveCallback;

    elements.settingsBtn?.addEventListener('click', toggle);
    elements.settingsCloseBtn?.addEventListener('click', toggle);
    elements.settingsTabs?.addEventListener('click', _handleSettingsTabClick);
    
    elements.saveAppearanceBtn?.addEventListener('click', async () => {
        const form = document.getElementById('appearance-settings-form');
        if (!form) return;
        const newSettings = {
            theme: form.elements['theme'].value,
            transparency: form.elements['transparency'].value,
            textSize: form.elements['textSize'].value,
            spacing: form.elements['spacing'].value,
            tooltips_enabled: elements.tooltipToggle.checked
        };
        const response = await fetch('/api/settings/appearance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newSettings)
        });
        const result = await response.json();
        if (result.status === 'success') {
            document.body.className = ''; 
            _previewAppearanceSettings();
            if (elements.statusMessage) elements.statusMessage.textContent = 'Appearance settings updated.';
        }
    });

    elements.purgeVoidBtn?.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to permanently delete ALL voided documents? This action cannot be undone.')) return;
        if (elements.statusMessage) elements.statusMessage.textContent = 'Purging voided documents...';
        const response = await fetch('/api/settings/purge', { method: 'POST' });
        const result = await response.json();
        if (elements.statusMessage) elements.statusMessage.textContent = result.message || 'Purge complete.';
        loadArchiveFn();
    });

    if (elements.settingsPanel) {
        elements.settingsPanel.querySelector('#appearance-settings-form')?.addEventListener('change', _previewAppearanceSettings);
    }
}

// Function to update local data when the main archive changes
export function updateData(newArchiveData) {
    archiveData = newArchiveData;
    const activeTab = elements.settingsTabs?.querySelector('.active')?.dataset.tab;
    if (activeTab === 'filemanager') {
        _renderVoidedDocsList();
    }
}
