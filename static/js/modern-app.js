// Modern King's Choice Management System JavaScript - Professional Edition

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Professional Card Animations
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.classList.add('card-hover');
        
        setTimeout(() => {
            card.style.transition = 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 150);
    });

    // Professional Button Enhancements
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.classList.add('btn-animated');
        
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px) scale(1.02)';
            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '';
        });
    });

    // Professional Form Enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Processing...';
                
                // Add shimmer effect
                submitBtn.style.background = 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)';
                submitBtn.style.backgroundSize = '200px 100%';
                submitBtn.style.animation = 'shimmer 1.5s infinite';
            }
        });
    });

    // Professional Table Enhancements
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        table.classList.add('table-hover');
        
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach((row, index) => {
            row.style.opacity = '0';
            row.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                row.style.transition = 'all 0.5s ease';
                row.style.opacity = '1';
                row.style.transform = 'translateX(0)';
            }, index * 100);
        });
    });

    // Professional Alert Animations
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.classList.add('slide-in-top');
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.style.transition = 'all 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // Professional Modal Enhancements
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            const modalDialog = this.querySelector('.modal-dialog');
            modalDialog.style.transform = 'scale(0.8)';
            modalDialog.style.opacity = '0';
            
            setTimeout(() => {
                modalDialog.style.transition = 'all 0.3s ease';
                modalDialog.style.transform = 'scale(1)';
                modalDialog.style.opacity = '1';
            }, 10);
        });
    });

    // Professional Dropdown Enhancements
    const dropdowns = document.querySelectorAll('.dropdown-menu');
    dropdowns.forEach(dropdown => {
        dropdown.classList.add('slide-in-top');
    });

    // Professional Badge Animations
    const badges = document.querySelectorAll('.badge');
    badges.forEach(badge => {
        badge.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.transition = 'all 0.2s ease';
        });
        
        badge.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Professional Progress Bar Animations
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width || bar.getAttribute('aria-valuenow') + '%';
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease';
            bar.style.width = width;
        }, 500);
    });

    // Professional Skeleton Loading
    const skeletonElements = document.querySelectorAll('.skeleton');
    skeletonElements.forEach(element => {
        element.style.background = 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)';
        element.style.backgroundSize = '200px 100%';
        element.style.animation = 'shimmer 1.5s infinite';
    });

    // Professional Floating Action Button
    const fabButtons = document.querySelectorAll('.fab');
    fabButtons.forEach(button => {
        button.classList.add('float');
        
        button.addEventListener('mouseenter', function() {
            this.classList.remove('float');
            this.style.transform = 'scale(1.1)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.classList.add('float');
            this.style.transform = 'scale(1)';
        });
    });

    // Professional Glow Effects
    const glowElements = document.querySelectorAll('.glow');
    glowElements.forEach(element => {
        element.classList.add('glow');
    });

    // Professional Scale In Effects
    const scaleElements = document.querySelectorAll('.scale-in');
    scaleElements.forEach(element => {
        element.classList.add('scale-in');
    });

    // Professional Bounce In Effects
    const bounceElements = document.querySelectorAll('.bounce-in');
    bounceElements.forEach(element => {
        element.classList.add('bounce-in');
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add smooth scrolling to anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add confirmation dialogs to delete buttons
    const deleteButtons = document.querySelectorAll('a[href*="delete"], button[onclick*="delete"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Add search functionality to tables
    const searchInputs = document.querySelectorAll('input[type="search"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.table-responsive') || this.closest('.container').querySelector('table');
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        });
    });

    // Add copy to clipboard functionality
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const text = this.getAttribute('data-copy');
            navigator.clipboard.writeText(text).then(() => {
                // Show success feedback
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="bi bi-check me-2"></i>Copied!';
                this.classList.add('btn-success');
                this.classList.remove('btn-outline-secondary');
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('btn-success');
                    this.classList.add('btn-outline-secondary');
                }, 2000);
            });
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) {
                    modal.hide();
                }
            }
        }
    });

    // Add progress bars for long operations
    function showProgress(message = 'Processing...') {
        const progressHtml = `
            <div class="progress-container position-fixed top-0 start-0 w-100" style="z-index: 9999;">
                <div class="progress" style="height: 4px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" style="width: 100%"></div>
                </div>
                <div class="text-center mt-2">
                    <small class="text-muted">${message}</small>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', progressHtml);
    }

    function hideProgress() {
        const progressContainer = document.querySelector('.progress-container');
        if (progressContainer) {
            progressContainer.remove();
        }
    }

    // Make progress functions globally available
    window.showProgress = showProgress;
    window.hideProgress = hideProgress;

    // Add theme switching functionality
    function switchTheme(theme) {
        document.body.className = document.body.className.replace(/theme-\w+/, '');
        document.body.classList.add(`theme-${theme}`);
        localStorage.setItem('theme', theme);
    }

    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'modern';
    switchTheme(savedTheme);

    // Add theme switcher if it exists
    const themeSwitcher = document.querySelector('[data-theme-switcher]');
    if (themeSwitcher) {
        themeSwitcher.addEventListener('change', function() {
            switchTheme(this.value);
        });
    }

    // Add data refresh functionality
    function refreshData() {
        const refreshButtons = document.querySelectorAll('[data-refresh]');
        refreshButtons.forEach(button => {
            button.addEventListener('click', function() {
                const url = this.getAttribute('data-refresh');
                if (url) {
                    showProgress('Refreshing data...');
                    fetch(url)
                        .then(response => response.text())
                        .then(html => {
                            // Replace content
                            const newContent = new DOMParser().parseFromString(html, 'text/html');
                            const newData = newContent.querySelector('[data-refresh-target]');
                            const target = document.querySelector('[data-refresh-target]');
                            if (newData && target) {
                                target.innerHTML = newData.innerHTML;
                            }
                            hideProgress();
                        })
                        .catch(error => {
                            console.error('Error refreshing data:', error);
                            hideProgress();
                        });
                }
            });
        });
    }

    refreshData();

    // Add auto-save functionality for forms
    const autoSaveForms = document.querySelectorAll('form[data-auto-save]');
    autoSaveForms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                const formData = new FormData(form);
                const data = Object.fromEntries(formData);
                
                // Save to localStorage
                localStorage.setItem(`autosave_${form.id}`, JSON.stringify(data));
                
                // Show auto-save indicator
                const indicator = document.querySelector('.auto-save-indicator');
                if (indicator) {
                    indicator.textContent = 'Auto-saved';
                    indicator.classList.add('text-success');
                    setTimeout(() => {
                        indicator.textContent = '';
                        indicator.classList.remove('text-success');
                    }, 2000);
                }
            });
        });

        // Load auto-saved data
        const savedData = localStorage.getItem(`autosave_${form.id}`);
        if (savedData) {
            try {
                const data = JSON.parse(savedData);
                Object.entries(data).forEach(([key, value]) => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input) {
                        input.value = value;
                    }
                });
            } catch (error) {
                console.error('Error loading auto-saved data:', error);
            }
        }
    });

    // Add notification system
    function showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(notification);
            bsAlert.close();
        }, duration);
    }

    // Make notification function globally available
    window.showNotification = showNotification;

    // Add drag and drop functionality for file uploads
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        const dropZone = input.closest('.file-drop-zone') || input.parentElement;
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            dropZone.classList.add('drag-over');
        }

        function unhighlight(e) {
            dropZone.classList.remove('drag-over');
        }

        dropZone.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            input.files = files;
            
            // Trigger change event
            const event = new Event('change', { bubbles: true });
            input.dispatchEvent(event);
        }
    });

    console.log('🎉 Modern King\'s Choice Management System initialized!');
});
