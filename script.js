// Paper Database
const paperDatabase = [
    {
        id: 1,
        name: "MultiArt Silk 90gr",
        weight: 90,
        dimensions: "360×315",
        finish: "silk",
        notes: "High-quality silk finish"
    },
    {
        id: 2,
        name: "G-Print 100gr",
        weight: 100,
        dimensions: "445×315",
        finish: "matte",
        notes: "Standard G-Print series"
    },
    {
        id: 3,
        name: "G-Print 130gr",
        weight: 130,
        dimensions: "320×252",
        finish: "matte",
        notes: "Heavy weight G-Print",
        corrections: {
            cross1: 0.2,
            cross2: -0.2,
            cross3: 0.1,
            cross4: -0.1
        }
    },
    {
        id: 4,
        name: "Arctic Volume White 130gr",
        weight: 130,
        dimensions: "320×252",
        finish: "white",
        notes: "Arctic series white"
    },
    {
        id: 5,
        name: "Arctic Volume Ice 130gr",
        weight: 130,
        dimensions: "320×252",
        finish: "ice",
        notes: "Arctic series ice finish"
    },
    {
        id: 6,
        name: "G-Print 170gr",
        weight: 170,
        dimensions: "320×252",
        finish: "matte",
        notes: "Extra heavy G-Print"
    },
    {
        id: 7,
        name: "Amber Graphic 140gr",
        weight: 140,
        dimensions: "355×252",
        finish: "matte",
        notes: "Amber Graphic series"
    },
    {
        id: 8,
        name: "Amber Graphic 140gr",
        weight: 140,
        dimensions: "355×310",
        finish: "matte",
        notes: "Amber Graphic series - larger format"
    },
    {
        id: 9,
        name: "Munken Premium Cream 115gr",
        weight: 115,
        dimensions: "355×310",
        finish: "cream",
        notes: "Premium Munken cream"
    },
    {
        id: 10,
        name: "Munken Pure 130gr",
        weight: 130,
        dimensions: "355×310",
        finish: "white",
        notes: "Munken Pure series"
    },
    {
        id: 11,
        name: "Amber Graphic 120gr",
        weight: 120,
        dimensions: "320×252",
        finish: "matte",
        notes: "Lighter Amber Graphic"
    },
    {
        id: 12,
        name: "Amber Graphic 100gr",
        weight: 100,
        dimensions: "320×252",
        finish: "matte",
        notes: "Lightest Amber Graphic"
    },
    {
        id: 13,
        name: "Munken Print Cream 80gr",
        weight: 80,
        dimensions: "320×252",
        finish: "cream",
        notes: "Light Munken Print"
    },
    {
        id: 14,
        name: "Magno Volume 150gr",
        weight: 150,
        dimensions: "487×320",
        finish: "matte",
        notes: "Large format Magno"
    },
    {
        id: 15,
        name: "Munken Lynx Rough 150gr",
        weight: 150,
        dimensions: "445×315",
        finish: "rough",
        notes: "Rough texture Munken"
    },
    {
        id: 16,
        name: "Munken Polar Rough 120gr",
        weight: 120,
        dimensions: "445×315",
        finish: "rough",
        notes: "Polar rough texture"
    }
];

// Global variables
let currentSettings = null;
let filteredPapers = [...paperDatabase];

// DOM Elements
const papersGrid = document.getElementById('papersGrid');
const searchInput = document.getElementById('searchInput');
const weightFilter = document.getElementById('weightFilter');
const finishFilter = document.getElementById('finishFilter');
const paperSelect = document.getElementById('paperSelect');
const quickPaperSelect = document.getElementById('quickPaperSelect');
const addPaperModal = document.getElementById('addPaperModal');
const addPaperForm = document.getElementById('addPaperForm');
const settingsDisplay = document.getElementById('settingsDisplay');

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    renderPapers();
    populatePaperSelects();
});

function initializeApp() {
    // Load saved corrections from localStorage
    loadSavedCorrections();
}

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            switchTab(item.dataset.tab);
        });
    });

    // Search and filters
    searchInput.addEventListener('input', filterPapers);
    weightFilter.addEventListener('change', filterPapers);
    finishFilter.addEventListener('change', filterPapers);

    // Add paper modal
    document.getElementById('addPaperBtn').addEventListener('click', () => {
        addPaperModal.classList.add('show');
    });

    document.getElementById('closeModal').addEventListener('click', () => {
        addPaperModal.classList.remove('show');
    });

    document.getElementById('cancelAdd').addEventListener('click', () => {
        addPaperModal.classList.remove('show');
    });

    addPaperForm.addEventListener('submit', addNewPaper);

    // Corrections
    document.getElementById('quickApplyBtn').addEventListener('click', quickApplySettings);
    document.getElementById('loadSettingsBtn').addEventListener('click', loadSavedSettings);
    document.getElementById('saveSettingsBtn').addEventListener('click', saveCurrentSettings);
}

function switchTab(tabName) {
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

function filterPapers() {
    const searchTerm = searchInput.value.toLowerCase();
    const weightFilterValue = weightFilter.value;
    const finishFilterValue = finishFilter.value;

    filteredPapers = paperDatabase.filter(paper => {
        const matchesSearch = paper.name.toLowerCase().includes(searchTerm) ||
                            paper.dimensions.toLowerCase().includes(searchTerm) ||
                            paper.notes.toLowerCase().includes(searchTerm);
        
        const matchesWeight = !weightFilterValue || paper.weight.toString() === weightFilterValue;
        const matchesFinish = !finishFilterValue || paper.finish === finishFilterValue;

        return matchesSearch && matchesWeight && matchesFinish;
    });

    renderPapers();
}

function renderPapers() {
    papersGrid.innerHTML = '';

    if (filteredPapers.length === 0) {
        papersGrid.innerHTML = '<div class="text-center"><p>No papers found matching your criteria.</p></div>';
        return;
    }

    filteredPapers.forEach(paper => {
        const paperCard = createPaperCard(paper);
        papersGrid.appendChild(paperCard);
    });
}

function createPaperCard(paper) {
    const card = document.createElement('div');
    card.className = 'paper-card';
    
    const hasCorrections = paper.corrections ? '✓' : '○';
    const correctionStatus = paper.corrections ? 'Saved' : 'Not saved';
    
    card.innerHTML = `
        <h3>${paper.name}</h3>
        <div class="paper-specs">
            <div class="spec-item">
                <span class="spec-label">Weight</span>
                <span class="spec-value">${paper.weight}gr</span>
            </div>
            <div class="spec-item">
                <span class="spec-label">Dimensions</span>
                <span class="spec-value">${paper.dimensions}</span>
            </div>
            <div class="spec-item">
                <span class="spec-label">Finish</span>
                <span class="spec-value">${paper.finish}</span>
            </div>
            <div class="spec-item">
                <span class="spec-label">Corrections</span>
                <span class="spec-value">${hasCorrections} ${correctionStatus}</span>
            </div>
        </div>
        <p class="mb-2">${paper.notes}</p>
        <div class="paper-actions">
            <button class="btn btn-primary btn-small" onclick="applyPaperSettings(${paper.id})">
                <i class="fas fa-play"></i>
                Apply Settings
            </button>
            <button class="btn btn-secondary btn-small" onclick="editPaperSettings(${paper.id})">
                <i class="fas fa-edit"></i>
                Edit
            </button>
        </div>
    `;
    
    return card;
}

function populatePaperSelects() {
    const selects = [paperSelect, quickPaperSelect];
    
    selects.forEach(select => {
        select.innerHTML = '<option value="">Choose a paper...</option>';
        paperDatabase.forEach(paper => {
            const option = document.createElement('option');
            option.value = paper.id;
            option.textContent = `${paper.name} (${paper.dimensions})`;
            select.appendChild(option);
        });
    });
}

function applyPaperSettings(paperId) {
    const paper = paperDatabase.find(p => p.id === paperId);
    if (!paper) return;

    if (paper.corrections) {
        currentSettings = {
            paper: paper,
            corrections: paper.corrections
        };
        updateSettingsDisplay();
        showNotification(`Applied settings for ${paper.name}`, 'success');
    } else {
        showNotification(`No saved settings for ${paper.name}`, 'warning');
    }
}

function quickApplySettings() {
    const paperId = parseInt(quickPaperSelect.value);
    if (!paperId) {
        showNotification('Please select a paper type', 'warning');
        return;
    }
    
    applyPaperSettings(paperId);
}

function loadSavedSettings() {
    const paperId = parseInt(paperSelect.value);
    if (!paperId) {
        showNotification('Please select a paper type', 'warning');
        return;
    }

    const paper = paperDatabase.find(p => p.id === paperId);
    if (!paper || !paper.corrections) {
        showNotification('No saved settings for this paper', 'warning');
        return;
    }

    // Fill the form with saved settings
    document.getElementById('cross1').value = paper.corrections.cross1;
    document.getElementById('cross2').value = paper.corrections.cross2;
    document.getElementById('cross3').value = paper.corrections.cross3;
    document.getElementById('cross4').value = paper.corrections.cross4;

    showNotification(`Loaded settings for ${paper.name}`, 'success');
}

function saveCurrentSettings() {
    const paperId = parseInt(paperSelect.value);
    if (!paperId) {
        showNotification('Please select a paper type', 'warning');
        return;
    }

    const corrections = {
        cross1: parseFloat(document.getElementById('cross1').value) || 0,
        cross2: parseFloat(document.getElementById('cross2').value) || 0,
        cross3: parseFloat(document.getElementById('cross3').value) || 0,
        cross4: parseFloat(document.getElementById('cross4').value) || 0
    };

    // Update paper in database
    const paperIndex = paperDatabase.findIndex(p => p.id === paperId);
    if (paperIndex !== -1) {
        paperDatabase[paperIndex].corrections = corrections;
        saveCorrectionsToStorage();
        renderPapers(); // Refresh the display
        showNotification('Settings saved successfully!', 'success');
    }
}

function updateSettingsDisplay() {
    if (!currentSettings) {
        settingsDisplay.innerHTML = '<p class="no-settings">No settings applied yet</p>';
        return;
    }

    const { paper, corrections } = currentSettings;
    settingsDisplay.innerHTML = `
        <div class="settings-grid">
            <div class="setting-item">
                <span class="setting-label">Paper:</span>
                <span class="setting-value">${paper.name}</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Dimensions:</span>
                <span class="setting-value">${paper.dimensions}</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Cross 1:</span>
                <span class="setting-value">${corrections.cross1 > 0 ? '+' : ''}${corrections.cross1}</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Cross 2:</span>
                <span class="setting-value">${corrections.cross2 > 0 ? '+' : ''}${corrections.cross2}</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Cross 3:</span>
                <span class="setting-value">${corrections.cross3 > 0 ? '+' : ''}${corrections.cross3}</span>
            </div>
            <div class="setting-item">
                <span class="setting-label">Cross 4:</span>
                <span class="setting-value">${corrections.cross4 > 0 ? '+' : ''}${corrections.cross4}</span>
            </div>
        </div>
    `;
}

function editPaperSettings(paperId) {
    const paper = paperDatabase.find(p => p.id === paperId);
    if (!paper) return;

    // Switch to corrections tab
    switchTab('corrections');
    
    // Select the paper
    paperSelect.value = paperId;
    
    // Load existing settings if available
    if (paper.corrections) {
        document.getElementById('cross1').value = paper.corrections.cross1;
        document.getElementById('cross2').value = paper.corrections.cross2;
        document.getElementById('cross3').value = paper.corrections.cross3;
        document.getElementById('cross4').value = paper.corrections.cross4;
    }
}

function addNewPaper(e) {
    e.preventDefault();
    
    const newPaper = {
        id: paperDatabase.length + 1,
        name: document.getElementById('paperName').value,
        weight: parseInt(document.getElementById('paperWeight').value),
        dimensions: document.getElementById('paperDimensions').value,
        finish: document.getElementById('paperFinish').value,
        notes: document.getElementById('paperNotes').value
    };

    paperDatabase.push(newPaper);
    populatePaperSelects();
    renderPapers();
    addPaperModal.classList.remove('show');
    addPaperForm.reset();
    
    showNotification('Paper added successfully!', 'success');
}

// Local Storage functions
function saveCorrectionsToStorage() {
    const papersWithCorrections = paperDatabase.filter(paper => paper.corrections);
    localStorage.setItem('paperCorrections', JSON.stringify(papersWithCorrections));
}

function loadSavedCorrections() {
    const saved = localStorage.getItem('paperCorrections');
    if (saved) {
        const papersWithCorrections = JSON.parse(saved);
        papersWithCorrections.forEach(savedPaper => {
            const paperIndex = paperDatabase.findIndex(p => p.id === savedPaper.id);
            if (paperIndex !== -1) {
                paperDatabase[paperIndex].corrections = savedPaper.corrections;
            }
        });
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '1rem 1.5rem',
        borderRadius: '0.5rem',
        color: 'white',
        fontWeight: '500',
        zIndex: '10000',
        maxWidth: '300px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        transform: 'translateX(100%)',
        transition: 'transform 0.3s ease'
    });

    // Set background color based on type
    const colors = {
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6'
    };
    notification.style.backgroundColor = colors[type] || colors.info;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}