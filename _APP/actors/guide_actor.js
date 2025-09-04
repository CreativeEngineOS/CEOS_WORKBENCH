/*
    CEOS Workbench - Guide Actor
    Version: 1.0.0
    Date: 2025-09-03
    Copyright: © 2025, Bastiaan Slabbers/Creative Engine OS. All rights reserved.

    Purpose:
    Manages the functionality of the interactive help guide modal.
*/

// --- Module-level State ---
let elements = {};
let guideRegistry = {};
let currentGuide = null;
let currentStep = 0;
let activeGuidePanel = null;

/**
 * Loads the SVG visual for the current guide from the server.
 * @private
 */
async function _loadGuideVisual() {
    if (!activeGuidePanel) return;
    const visualPanel = activeGuidePanel.querySelector('.guide-visual-panel');
    if (!currentGuide || !currentGuide.visual || !visualPanel) {
        if (visualPanel) {
            visualPanel.innerHTML = '<p class="text-gray-500 italic p-4">No visual for this guide.</p>';
        }
        return;
    }
    try {
        const requestUrl = `/api/guide/visual/${currentGuide.visual}`;
        const response = await fetch(requestUrl);
        if (!response.ok) throw new Error(`Server responded with status: ${response.status}`);
        const svgText = await response.text();
        visualPanel.innerHTML = svgText;
        _highlightCurrentStepNode();
    } catch (error) {
        console.error("Error loading visual:", error);
        visualPanel.innerHTML = `<p class="text-red-400 p-4">Could not load visual.<br><span class="text-xs text-gray-500">${error.message}</span></p>`;
    }
}

/**
 * Loads the markdown content for the current guide step from the server.
 * @private
 */
async function _loadGuideStep() {
    if (!currentGuide || !activeGuidePanel) return;
    const contentPanel = activeGuidePanel.querySelector('.guide-step-content');
    const guideId = Object.keys(guideRegistry).find(key => guideRegistry[key] === currentGuide);
    try {
        const response = await fetch(`/api/guide/step/${guideId}/${currentStep}`);
        if (!response.ok) throw new Error(`Server responded with status: ${response.status}`);
        const result = await response.json();
        if (result.status !== 'success') throw new Error(result.message);
        const converter = new showdown.Converter();
        contentPanel.innerHTML = converter.makeHtml(result.data.content);
    } catch (error) {
        console.error("Error loading guide step:", error);
        contentPanel.innerHTML = `<p class="text-red-400">Could not load step content.<br><span class="text-xs text-gray-500">${error.message}</span></p>`;
    }
    _updateGuideUI();
}

/**
 * Updates the guide's UI elements like titles, step indicators, and button states.
 * @private
 */
function _updateGuideUI() {
    if (!currentGuide || !activeGuidePanel) return;
    
    const titleEl = elements.guideModal.querySelector('#guide-title');
    const indicatorEl = activeGuidePanel.querySelector('.guide-step-indicator');
    const prevBtn = activeGuidePanel.querySelector('.guide-prev-btn');
    const nextBtn = activeGuidePanel.querySelector('.guide-next-btn');

    if (titleEl) titleEl.textContent = currentGuide.title;
    if (indicatorEl) indicatorEl.textContent = `Step ${currentStep} / ${currentGuide.totalSteps}`;
    if (prevBtn) prevBtn.disabled = currentStep <= 1;
    if (nextBtn) nextBtn.disabled = currentStep >= currentGuide.totalSteps;
    _highlightCurrentStepNode();
}

/**
 * Highlights the current step's node in the SVG visual.
 * @private
 */
function _highlightCurrentStepNode() {
    if (!activeGuidePanel) return;
    const visualPanel = activeGuidePanel.querySelector('.guide-visual-panel');
    if (!visualPanel) return;
    const svg = visualPanel.querySelector('svg');
    if (!svg) return;
    svg.querySelectorAll('.node').forEach(node => {
        const shape = node.querySelector('ellipse, polygon, rect, path');
        if (shape) {
            shape.setAttribute('stroke', '#9ca3af');
            shape.setAttribute('stroke-width', '2');
        }
    });
    const currentNode = svg.querySelector(`#node-step-${currentStep}`);
    if (currentNode) {
        const shape = currentNode.querySelector('ellipse, polygon, rect, path');
        if (shape) {
            shape.setAttribute('stroke', 'var(--brand-color-orange)');
            shape.setAttribute('stroke-width', '3');
        }
    }
}

/**
 * Handles clicks on the next/previous navigation buttons in the guide.
 * @param {Event} e - The click event.
 * @private
 */
function _handleGuideNav(e) {
    if (!currentGuide) return;
    const direction = e.target.classList.contains('guide-next-btn') ? 'next' : 'prev';
    if (direction === 'next' && currentStep < currentGuide.totalSteps) {
        currentStep++;
    } else if (direction === 'prev' && currentStep > 1) {
        currentStep--;
    }
    _loadGuideStep();
}

/**
 * Handles clicks on the guide selection tabs (e.g., "Ingestion", "Editing").
 * @param {Event} e - The click event.
 * @private
 */
function _handleGuideTabClick(e) {
    const tabButton = e.target.closest('#guide-modal .settings-tab-btn');
    if (!tabButton) return;
    showGuide(tabButton.dataset.tab);
}

/**
 * Hides the guide modal from view.
 */
export function hideGuide() {
    if (elements.guideModal) elements.guideModal.classList.add('hidden');
    currentGuide = null;
    currentStep = 0;
    activeGuidePanel = null;
}

/**
 * Displays the guide modal and loads the content for a specific guide.
 * @param {string} guideId - The ID of the guide to show (e.g., "ingestion").
 */
export function showGuide(guideId) {
    currentGuide = guideRegistry[guideId];
    if (!currentGuide) {
        console.error(`Guide with ID "${guideId}" not found.`);
        return;
    }

    document.querySelectorAll('#guide-modal .settings-tab-btn').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('#guide-modal .guide-tab-panel').forEach(p => p.classList.remove('active'));
    
    activeGuidePanel = document.getElementById(guideId);
    const activeButton = elements.guideModal.querySelector(`.settings-tab-btn[data-tab="${guideId}"]`);
    
    if (activeGuidePanel) activeGuidePanel.classList.add('active');
    if (activeButton) activeButton.classList.add('active');

    currentStep = 1;
    if (elements.guideModal) elements.guideModal.classList.remove('hidden');
    _loadGuideVisual();
    _loadGuideStep();
}

/**
 * Initializes the Guide Actor.
 * @param {object} elementRefs - A dictionary of DOM element references from the main actor.
 * @param {object} registryData - The guide registry data loaded from JSON.
 */
export function init(elementRefs, registryData) {
    elements = elementRefs;
    guideRegistry = registryData;

    if (elements.guideModal) {
        elements.helpBtn?.addEventListener('click', () => showGuide('ingestion'));
        elements.guideCloseBtn?.addEventListener('click', hideGuide);
        elements.guideModal.querySelectorAll('.guide-navigation').forEach(nav => {
            nav.querySelector('.guide-prev-btn')?.addEventListener('click', _handleGuideNav);
            nav.querySelector('.guide-next-btn')?.addEventListener('click', _handleGuideNav);
        });
        elements.guideModal.querySelector('.guide-tabs')?.addEventListener('click', _handleGuideTabClick);
    } else {
        console.warn("GuideActor: Guide Modal element not found. Guide functionality will be disabled.");
    }
}