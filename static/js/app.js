/* King's Choice Management - JavaScript Application */

// Application namespace
const KingsChoice = {
    // Configuration
    config: {
        refreshInterval: 60000, // 60 seconds (reduced frequency)
        apiBaseUrl: '/api',
        debug: false,
        cacheTimeout: 30000, // 30 seconds cache
        maxRetries: 3
    },
    
    // Utility functions
    utils: {
        // Show loading spinner
        showLoading: function(element) {
            if (element) {
                const spinner = document.createElement('div');
                spinner.className = 'loading';
                spinner.setAttribute('data-loading', 'true');
                element.appendChild(spinner);
            }
        },
        
        // Hide loading spinner
        hideLoading: function(element) {
            if (element) {
                const spinner = element.querySelector('[data-loading="true"]');
                if (spinner) {
                    spinner.remove();
                }
            }
        },
        
        // Format date for display
        formatDate: function(dateString) {
            try {
                const date = new Date(dateString);
                return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
            } catch (e) {
                return dateString;
            }
        },
        
        // Show notification
        showNotification: function(message, type = 'info', duration = 5000) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}-fill me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            // Insert at top of main container
            const container = document.querySelector('.container');
            if (container) {
                container.insertBefore(alertDiv, container.firstChild);
                
                // Auto-remove after duration
                setTimeout(() => {
                    if (alertDiv.parentNode) {
                        alertDiv.remove();
                    }
                }, duration);
            }
        },
        
        // Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Log function (respects debug mode)
        log: function(message, data = null) {
            if (KingsChoice.config.debug) {
                console.log(`[KingsChoice] ${message}`, data || '');
            }
        }
    },
    
    // API functions
    api: {
        // Cache for API responses
        cache: new Map(),
        
        // Generic API call with caching
        call: async function(endpoint, options = {}) {
            try {
                const url = KingsChoice.config.apiBaseUrl + endpoint;
                const cacheKey = `${url}_${JSON.stringify(options)}`;
                
                // Check cache first
                if (this.cache.has(cacheKey)) {
                    const cached = this.cache.get(cacheKey);
                    if (Date.now() - cached.timestamp < KingsChoice.config.cacheTimeout) {
                        KingsChoice.utils.log('Using cached response for:', endpoint);
                        return cached.data;
                    }
                }
                
                const response = await fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'API call failed');
                }
                
                // Cache successful responses
                this.cache.set(cacheKey, {
                    data: data,
                    timestamp: Date.now()
                });
                
                return data;
            } catch (error) {
                KingsChoice.utils.log('API Error:', error);
                throw error;
            }
        },
        
        // Clear cache
        clearCache: function() {
            this.cache.clear();
            KingsChoice.utils.log('API cache cleared');
        },
        
        // Get dashboard data
        getDashboardData: async function() {
            return await this.call('/dashboard-data');
        },
        
        // Get players
        getPlayers: async function() {
            return await this.call('/players/list');
        },
        
        // Get alliances
        getAlliances: async function() {
            return await this.call('/alliances/list');
        },
        
        // Get events
        getEvents: async function() {
            return await this.call('/events/list');
        },
        
        // Get rotation status
        getRotationStatus: async function() {
            const [playerStatus, allianceStatus] = await Promise.all([
                this.call('/players/rotation-status'),
                this.call('/alliances/rotation-status')
            ]);
            
            return {
                players: playerStatus,
                alliances: allianceStatus
            };
        }
    },
    
    // UI components
    ui: {
        // Initialize all UI components
        init: function() {
            this.initTooltips();
            this.initPopovers();
            this.initFormValidation();
            this.initTableSorting();
            this.initSearchFilters();
        },
        
        // Initialize Bootstrap tooltips
        initTooltips: function() {
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        },
        
        // Initialize Bootstrap popovers
        initPopovers: function() {
            const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
            popoverTriggerList.map(function (popoverTriggerEl) {
                return new bootstrap.Popover(popoverTriggerEl);
            });
        },
        
        // Enhanced form validation
        initFormValidation: function() {
            const forms = document.querySelectorAll('.needs-validation');
            Array.prototype.slice.call(forms).forEach(function (form) {
                form.addEventListener('submit', function (event) {
                    if (!form.checkValidity()) {
                        event.preventDefault();
                        event.stopPropagation();
                    }
                    form.classList.add('was-validated');
                }, false);
            });
            
            // Real-time validation for specific fields
            const nameInputs = document.querySelectorAll('input[name="name"]');
            nameInputs.forEach(input => {
                input.addEventListener('input', this.validateNameInput.bind(this));
            });
        },
        
        // Validate name input
        validateNameInput: function(event) {
            const input = event.target;
            const value = input.value.trim();
            
            if (value.length === 0) {
                input.setCustomValidity('Name is required');
                input.classList.add('is-invalid');
                input.classList.remove('is-valid');
            } else if (value.length > 100) {
                input.setCustomValidity('Name cannot exceed 100 characters');
                input.classList.add('is-invalid');
                input.classList.remove('is-valid');
            } else {
                input.setCustomValidity('');
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            }
        },
        
        // Initialize table sorting
        initTableSorting: function() {
            const tables = document.querySelectorAll('.table-sortable');
            tables.forEach(table => {
                const headers = table.querySelectorAll('th[data-sort]');
                headers.forEach(header => {
                    header.style.cursor = 'pointer';
                    header.addEventListener('click', this.sortTable.bind(this));
                });
            });
        },
        
        // Sort table by column
        sortTable: function(event) {
            const header = event.target;
            const table = header.closest('table');
            const column = header.getAttribute('data-sort');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            // Determine sort direction
            const currentOrder = header.getAttribute('data-order') || 'asc';
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
            
            // Sort rows
            rows.sort((a, b) => {
                const aValue = a.querySelector(`td:nth-child(${header.cellIndex + 1})`).textContent.trim();
                const bValue = b.querySelector(`td:nth-child(${header.cellIndex + 1})`).textContent.trim();
                
                if (newOrder === 'asc') {
                    return aValue.localeCompare(bValue, undefined, { numeric: true });
                } else {
                    return bValue.localeCompare(aValue, undefined, { numeric: true });
                }
            });
            
            // Update table
            rows.forEach(row => tbody.appendChild(row));
            
            // Update header indicators
            table.querySelectorAll('th').forEach(th => {
                th.removeAttribute('data-order');
                th.classList.remove('sort-asc', 'sort-desc');
            });
            
            header.setAttribute('data-order', newOrder);
            header.classList.add(`sort-${newOrder}`);
        },
        
        // Initialize search filters
        initSearchFilters: function() {
            const searchInputs = document.querySelectorAll('[data-search-target]');
            searchInputs.forEach(input => {
                input.addEventListener('input', 
                    KingsChoice.utils.debounce(this.filterTable.bind(this), 300)
                );
            });
        },
        
        // Filter table based on search
        filterTable: function(event) {
            const input = event.target;
            const searchTerm = input.value.toLowerCase();
            const targetSelector = input.getAttribute('data-search-target');
            const table = document.querySelector(targetSelector);
            
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        },
        
        // Update rotation status displays
        updateRotationStatus: async function() {
            try {
                const status = await KingsChoice.api.getRotationStatus();
                
                // Update player rotation status
                const playerStatusElement = document.getElementById('player-rotation-status');
                if (playerStatusElement) {
                    this.renderRotationStatus(playerStatusElement, status.players, 'MVP');
                }
                
                // Update alliance rotation status
                const allianceStatusElement = document.getElementById('alliance-rotation-status');
                if (allianceStatusElement) {
                    this.renderRotationStatus(allianceStatusElement, status.alliances, 'Winner');
                }
                
            } catch (error) {
                KingsChoice.utils.log('Failed to update rotation status:', error);
            }
        },
        
        // Render rotation status
        renderRotationStatus: function(element, status, type) {
            if (!status.success) return;
            
            const canAssign = status[`can_assign_${type.toLowerCase()}`];
            const eligible = status[`eligible_${type.toLowerCase() === 'mvp' ? 'players' : 'alliances'}`];
            
            element.innerHTML = `
                <div class="alert alert-${canAssign ? 'success' : 'warning'} d-flex align-items-center mb-0">
                    <i class="bi bi-${canAssign ? 'check-circle-fill' : 'exclamation-triangle-fill'} me-2"></i>
                    <div>
                        <strong>${type} Assignment ${canAssign ? 'Available' : 'Locked'}</strong><br>
                        <small>${canAssign ? 
                            `Eligible: ${eligible.map(e => e.name).join(', ')}` : 
                            `Complete current rotation first`
                        }</small>
                    </div>
                </div>
            `;
        }
    },
    
    // Auto-refresh functionality
    autoRefresh: {
        intervalId: null,
        
        start: function() {
            if (this.intervalId) return; // Already running
            
            this.intervalId = setInterval(() => {
                this.refresh();
            }, KingsChoice.config.refreshInterval);
            
            KingsChoice.utils.log('Auto-refresh started');
        },
        
        stop: function() {
            if (this.intervalId) {
                clearInterval(this.intervalId);
                this.intervalId = null;
                KingsChoice.utils.log('Auto-refresh stopped');
            }
        },
        
        refresh: async function() {
            try {
                // Only refresh if user is not actively interacting
                if (document.hidden) return;
                
                // Check if user is actively typing or interacting
                if (document.activeElement && 
                    (document.activeElement.tagName === 'INPUT' || 
                     document.activeElement.tagName === 'TEXTAREA' ||
                     document.activeElement.isContentEditable)) {
                    return; // Skip refresh if user is typing
                }
                
                // Update rotation status on relevant pages
                const currentPage = window.location.pathname;
                if (currentPage.includes('/players') || currentPage.includes('/alliances')) {
                    await KingsChoice.ui.updateRotationStatus();
                }
                
                // Update dashboard data if on dashboard
                if (currentPage === '/' || currentPage.includes('/dashboard')) {
                    await this.refreshDashboard();
                }
                
            } catch (error) {
                KingsChoice.utils.log('Auto-refresh error:', error);
            }
        },
        
        refreshDashboard: async function() {
            try {
                const data = await KingsChoice.api.getDashboardData();
                if (data.success) {
                    // Update current MVP display
                    const mvpElement = document.getElementById('current-mvp-display');
                    if (mvpElement && data.current_mvp) {
                        mvpElement.textContent = data.current_mvp.name;
                    }
                    
                    // Update current winner display
                    const winnerElement = document.getElementById('current-winner-display');
                    if (winnerElement && data.current_winner) {
                        winnerElement.textContent = data.current_winner.name;
                    }
                }
            } catch (error) {
                KingsChoice.utils.log('Dashboard refresh error:', error);
            }
        }
    },
    
    // Initialize the application
    init: function() {
        KingsChoice.utils.log('Initializing King\'s Choice Management App');
        
        // Initialize UI components
        this.ui.init();
        
        // Start auto-refresh on interactive pages
        const autoRefreshPages = ['/', '/players', '/alliances', '/dashboard'];
        if (autoRefreshPages.some(page => window.location.pathname.includes(page))) {
            this.autoRefresh.start();
        }
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.autoRefresh.stop();
            } else {
                this.autoRefresh.start();
            }
        });
        
        // Handle beforeunload to cleanup
        window.addEventListener('beforeunload', () => {
            this.autoRefresh.stop();
        });
        
        KingsChoice.utils.log('Application initialized successfully');
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    KingsChoice.init();
});

// Global functions for template usage
window.KingsChoice = KingsChoice;