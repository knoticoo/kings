/**
 * HTML Content Categorizer
 * 
 * Automatically detects and categorizes HTML tags when pasting content
 * into the guide editor. Provides visual organization and structure.
 */

class HTMLCategorizer {
    constructor() {
        this.tagCategories = {
            headings: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
            lists: ['ul', 'ol', 'li'],
            text: ['p', 'span', 'div', 'strong', 'b', 'em', 'i', 'u'],
            media: ['img', 'video', 'audio'],
            tables: ['table', 'tr', 'td', 'th', 'thead', 'tbody'],
            links: ['a'],
            structure: ['section', 'article', 'header', 'footer', 'nav', 'aside'],
            formatting: ['br', 'hr', 'blockquote', 'pre', 'code']
        };
        
        this.categoryColors = {
            headings: '#007bff',
            lists: '#28a745',
            text: '#6c757d',
            media: '#fd7e14',
            tables: '#20c997',
            links: '#e83e8c',
            structure: '#6f42c1',
            formatting: '#ffc107'
        };
        
        this.categoryIcons = {
            headings: 'bi-type-h1',
            lists: 'bi-list-ul',
            text: 'bi-fonts',
            media: 'bi-image',
            tables: 'bi-table',
            links: 'bi-link-45deg',
            structure: 'bi-layout-sidebar',
            formatting: 'bi-type'
        };
    }

    /**
     * Categorize HTML content and return structured data
     */
    categorizeContent(htmlContent) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlContent, 'text/html');
        const categorizedElements = [];
        
        // Process all elements in the content
        const allElements = doc.querySelectorAll('*');
        
        allElements.forEach((element, index) => {
            const tagName = element.tagName.toLowerCase();
            const category = this.getTagCategory(tagName);
            
            if (category) {
                categorizedElements.push({
                    index: index,
                    tagName: tagName,
                    category: category,
                    content: element.outerHTML,
                    textContent: element.textContent.trim(),
                    attributes: this.getElementAttributes(element),
                    level: this.getElementLevel(element)
                });
            }
        });
        
        return {
            elements: categorizedElements,
            summary: this.generateSummary(categorizedElements),
            structure: this.generateStructure(categorizedElements)
        };
    }

    /**
     * Get the category for a specific HTML tag
     */
    getTagCategory(tagName) {
        for (const [category, tags] of Object.entries(this.tagCategories)) {
            if (tags.includes(tagName)) {
                return category;
            }
        }
        return 'unknown';
    }

    /**
     * Get element attributes as an object
     */
    getElementAttributes(element) {
        const attributes = {};
        for (const attr of element.attributes) {
            attributes[attr.name] = attr.value;
        }
        return attributes;
    }

    /**
     * Determine the hierarchical level of an element
     */
    getElementLevel(element) {
        if (this.tagCategories.headings.includes(element.tagName.toLowerCase())) {
            return parseInt(element.tagName.charAt(1));
        }
        return 0;
    }

    /**
     * Generate a summary of the categorized content
     */
    generateSummary(elements) {
        const summary = {};
        
        elements.forEach(element => {
            if (!summary[element.category]) {
                summary[element.category] = {
                    count: 0,
                    tags: new Set()
                };
            }
            summary[element.category].count++;
            summary[element.category].tags.add(element.tagName);
        });
        
        // Convert Set to Array for JSON serialization
        Object.keys(summary).forEach(category => {
            summary[category].tags = Array.from(summary[category].tags);
        });
        
        return summary;
    }

    /**
     * Generate a hierarchical structure of the content
     */
    generateStructure(elements) {
        const structure = [];
        let currentSection = null;
        
        elements.forEach(element => {
            if (element.category === 'headings') {
                currentSection = {
                    heading: element,
                    content: [],
                    level: element.level
                };
                structure.push(currentSection);
            } else if (currentSection) {
                currentSection.content.push(element);
            } else {
                // Content before any heading
                if (!structure.length || structure[structure.length - 1].heading) {
                    structure.push({
                        heading: null,
                        content: [element],
                        level: 0
                    });
                } else {
                    structure[structure.length - 1].content.push(element);
                }
            }
        });
        
        return structure;
    }

    /**
     * Create visual representation of categorized content
     */
    createVisualRepresentation(categorizedData) {
        const container = document.createElement('div');
        container.className = 'html-categorizer-container';
        
        // Add summary section
        const summarySection = this.createSummarySection(categorizedData.summary);
        container.appendChild(summarySection);
        
        // Add structure section
        const structureSection = this.createStructureSection(categorizedData.structure);
        container.appendChild(structureSection);
        
        return container;
    }

    /**
     * Create summary section showing tag counts by category
     */
    createSummarySection(summary) {
        const section = document.createElement('div');
        section.className = 'categorizer-summary mb-3';
        
        const title = document.createElement('h6');
        title.textContent = 'Content Analysis';
        title.className = 'text-muted mb-2';
        section.appendChild(title);
        
        const summaryGrid = document.createElement('div');
        summaryGrid.className = 'row g-2';
        
        Object.entries(summary).forEach(([category, data]) => {
            const col = document.createElement('div');
            col.className = 'col-6 col-md-3';
            
            const card = document.createElement('div');
            card.className = 'card border-0 bg-light';
            
            const cardBody = document.createElement('div');
            cardBody.className = 'card-body p-2 text-center';
            
            const icon = document.createElement('i');
            icon.className = `bi ${this.categoryIcons[category]} text-${this.getCategoryColorClass(category)}`;
            icon.style.fontSize = '1.2rem';
            
            const count = document.createElement('div');
            count.className = 'fw-bold';
            count.textContent = data.count;
            
            const label = document.createElement('div');
            label.className = 'small text-muted text-capitalize';
            label.textContent = category;
            
            cardBody.appendChild(icon);
            cardBody.appendChild(count);
            cardBody.appendChild(label);
            card.appendChild(cardBody);
            col.appendChild(card);
            summaryGrid.appendChild(col);
        });
        
        section.appendChild(summaryGrid);
        return section;
    }

    /**
     * Create structure section showing hierarchical organization
     */
    createStructureSection(structure) {
        const section = document.createElement('div');
        section.className = 'categorizer-structure';
        
        const title = document.createElement('h6');
        title.textContent = 'Content Structure';
        title.className = 'text-muted mb-2';
        section.appendChild(title);
        
        const structureList = document.createElement('div');
        structureList.className = 'list-group list-group-flush';
        
        structure.forEach((section, index) => {
            const item = document.createElement('div');
            item.className = 'list-group-item border-0 px-0';
            
            if (section.heading) {
                const headingDiv = document.createElement('div');
                headingDiv.className = 'd-flex align-items-center mb-1';
                
                const icon = document.createElement('i');
                icon.className = `bi ${this.categoryIcons.headings} me-2`;
                icon.style.color = this.categoryColors.headings;
                
                const headingText = document.createElement('span');
                headingText.className = 'fw-bold';
                headingText.textContent = section.heading.textContent;
                
                const level = document.createElement('span');
                level.className = 'badge bg-primary ms-2';
                level.textContent = `H${section.heading.level}`;
                
                headingDiv.appendChild(icon);
                headingDiv.appendChild(headingText);
                headingDiv.appendChild(level);
                item.appendChild(headingDiv);
            }
            
            if (section.content.length > 0) {
                const contentDiv = document.createElement('div');
                contentDiv.className = 'ms-4';
                
                const contentSummary = this.createContentSummary(section.content);
                contentDiv.appendChild(contentSummary);
                item.appendChild(contentDiv);
            }
            
            structureList.appendChild(item);
        });
        
        section.appendChild(structureList);
        return section;
    }

    /**
     * Create summary of content within a section
     */
    createContentSummary(content) {
        const summary = {};
        content.forEach(element => {
            if (!summary[element.category]) {
                summary[element.category] = 0;
            }
            summary[element.category]++;
        });
        
        const summaryText = Object.entries(summary)
            .map(([category, count]) => `${count} ${category}`)
            .join(', ');
        
        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'small text-muted';
        summaryDiv.textContent = summaryText;
        
        return summaryDiv;
    }

    /**
     * Get Bootstrap color class for category
     */
    getCategoryColorClass(category) {
        const colorMap = {
            headings: 'primary',
            lists: 'success',
            text: 'secondary',
            media: 'warning',
            tables: 'info',
            links: 'danger',
            structure: 'dark',
            formatting: 'warning'
        };
        return colorMap[category] || 'secondary';
    }

    /**
     * Process pasted content and show categorization
     */
    processPastedContent(textarea, pastedContent) {
        // First, try to detect and format Discord-style text
        const formattedContent = this.formatDiscordText(pastedContent);
        
        // If content was formatted, update the textarea
        if (formattedContent !== pastedContent) {
            textarea.value = formattedContent;
            this.showMessage('Discord text has been automatically formatted!', 'success');
        }
        
        const categorizedData = this.categorizeContent(formattedContent);
        const visualRepresentation = this.createVisualRepresentation(categorizedData);
        
        // Find or create the categorization display area
        let displayArea = textarea.parentNode.querySelector('.html-categorizer-display');
        if (!displayArea) {
            displayArea = document.createElement('div');
            displayArea.className = 'html-categorizer-display mt-3';
            textarea.parentNode.appendChild(displayArea);
        }
        
        // Clear previous content and add new categorization
        displayArea.innerHTML = '';
        displayArea.appendChild(visualRepresentation);
        
        // Add action buttons
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'mt-2';
        
        const organizeBtn = document.createElement('button');
        organizeBtn.type = 'button';
        organizeBtn.className = 'btn btn-sm btn-outline-primary me-2';
        organizeBtn.innerHTML = '<i class="bi bi-sort-alpha-down me-1"></i>Organize Content';
        organizeBtn.onclick = () => this.organizeContent(textarea, categorizedData);
        
        const formatBtn = document.createElement('button');
        formatBtn.type = 'button';
        formatBtn.className = 'btn btn-sm btn-outline-success me-2';
        formatBtn.innerHTML = '<i class="bi bi-magic me-1"></i>Auto Format';
        formatBtn.onclick = () => this.autoFormatContent(textarea);
        
        const clearBtn = document.createElement('button');
        clearBtn.type = 'button';
        clearBtn.className = 'btn btn-sm btn-outline-secondary';
        clearBtn.innerHTML = '<i class="bi bi-x-circle me-1"></i>Clear Analysis';
        clearBtn.onclick = () => this.clearAnalysis(displayArea);
        
        actionsDiv.appendChild(organizeBtn);
        actionsDiv.appendChild(formatBtn);
        actionsDiv.appendChild(clearBtn);
        displayArea.appendChild(actionsDiv);
        
        return categorizedData;
    }

    /**
     * Organize content based on categorization
     */
    organizeContent(textarea, categorizedData) {
        let organizedContent = '';
        
        // Group content by sections (headings)
        categorizedData.structure.forEach(section => {
            if (section.heading) {
                organizedContent += section.heading.content + '\n\n';
            }
            
            // Group content by category within each section
            const contentByCategory = {};
            section.content.forEach(element => {
                if (!contentByCategory[element.category]) {
                    contentByCategory[element.category] = [];
                }
                contentByCategory[element.category].push(element);
            });
            
            // Add content in organized order
            const categoryOrder = ['text', 'lists', 'tables', 'media', 'links', 'formatting'];
            categoryOrder.forEach(category => {
                if (contentByCategory[category]) {
                    contentByCategory[category].forEach(element => {
                        organizedContent += element.content + '\n';
                    });
                    organizedContent += '\n';
                }
            });
            
            organizedContent += '\n';
        });
        
        // Update textarea with organized content
        textarea.value = organizedContent.trim();
        
        // Show success message
        this.showMessage('Content has been organized by structure and category!', 'success');
    }

    /**
     * Clear the analysis display
     */
    clearAnalysis(displayArea) {
        displayArea.innerHTML = '';
    }

    /**
     * Format Discord-style text to proper HTML
     */
    formatDiscordText(text) {
        let formatted = text;
        
        // Convert Discord markdown to HTML
        // Bold text: **text** or __text__
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>');
        
        // Italic text: *text* or _text_
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        formatted = formatted.replace(/_(.*?)_/g, '<em>$1</em>');
        
        // Code blocks: `text`
        formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>');
        
        // Headers: # Header, ## Header, etc.
        formatted = formatted.replace(/^### (.*$)/gm, '<h3>$1</h3>');
        formatted = formatted.replace(/^## (.*$)/gm, '<h2>$1</h2>');
        formatted = formatted.replace(/^# (.*$)/gm, '<h1>$1</h1>');
        
        // Convert tier list format
        formatted = this.formatTierList(formatted);
        
        // Convert line breaks to proper HTML
        formatted = formatted.replace(/\n\n/g, '</p><p>');
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Wrap in paragraph tags if not already wrapped
        if (!formatted.includes('<p>') && !formatted.includes('<h1>') && !formatted.includes('<h2>') && !formatted.includes('<h3>')) {
            formatted = '<p>' + formatted + '</p>';
        }
        
        return formatted;
    }
    
    /**
     * Format tier list structure
     */
    formatTierList(text) {
        let formatted = text;
        
        // Convert tier headers like `EX+`, `EX`, `SSS`, etc.
        const tierPatterns = [
            { pattern: /^`EX\+`$/gm, replacement: '<h2><strong>EX+</strong></h2>' },
            { pattern: /^`EX`$/gm, replacement: '<h2><strong>EX</strong></h2>' },
            { pattern: /^`SSS`$/gm, replacement: '<h2><strong>SSS</strong></h2>' },
            { pattern: /^`S`$/gm, replacement: '<h2><strong>S</strong></h2>' },
            { pattern: /^`A`$/gm, replacement: '<h2><strong>A</strong></h2>' },
            { pattern: /^`B`$/gm, replacement: '<h2><strong>B</strong></h2>' },
            { pattern: /^`C`$/gm, replacement: '<h2><strong>C</strong></h2>' },
            { pattern: /^`F`$/gm, replacement: '<h2><strong>F</strong></h2>' }
        ];
        
        tierPatterns.forEach(({ pattern, replacement }) => {
            formatted = formatted.replace(pattern, replacement);
        });
        
        // Convert list items that start with - to proper HTML lists
        const lines = formatted.split('\n');
        let inList = false;
        let result = [];
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Check if this is a list item
            if (line.startsWith('- ')) {
                if (!inList) {
                    result.push('<ul>');
                    inList = true;
                }
                result.push(`<li>${line.substring(2)}</li>`);
            } else {
                if (inList) {
                    result.push('</ul>');
                    inList = false;
                }
                result.push(line);
            }
        }
        
        // Close any open list
        if (inList) {
            result.push('</ul>');
        }
        
        return result.join('\n');
    }
    
    /**
     * Auto format content in textarea
     */
    autoFormatContent(textarea) {
        const currentContent = textarea.value;
        const formattedContent = this.formatDiscordText(currentContent);
        
        if (formattedContent !== currentContent) {
            textarea.value = formattedContent;
            this.showMessage('Content has been automatically formatted!', 'success');
            
            // Re-analyze the formatted content
            setTimeout(() => {
                this.processPastedContent(textarea, formattedContent);
            }, 100);
        } else {
            this.showMessage('No formatting changes needed.', 'info');
        }
    }
    
    /**
     * Show a temporary message
     */
    showMessage(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the form
        const form = document.querySelector('form');
        form.insertBefore(alertDiv, form.firstChild);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
}

// Initialize the categorizer when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const categorizer = new HTMLCategorizer();
    
    // Find all content textareas
    const contentTextareas = document.querySelectorAll('textarea[name="content"]');
    
    contentTextareas.forEach(textarea => {
        // Add paste event listener
        textarea.addEventListener('paste', function(e) {
            // Wait for paste to complete
            setTimeout(() => {
                const pastedContent = e.clipboardData.getData('text/html') || e.clipboardData.getData('text/plain');
                if (pastedContent && pastedContent.includes('<')) {
                    categorizer.processPastedContent(textarea, pastedContent);
                }
            }, 100);
        });
        
        // Add manual analysis button
        const analysisBtn = document.createElement('button');
        analysisBtn.type = 'button';
        analysisBtn.className = 'btn btn-sm btn-outline-info mt-2';
        analysisBtn.innerHTML = '<i class="bi bi-search me-1"></i>Analyze HTML Structure';
        analysisBtn.onclick = () => {
            if (textarea.value.trim()) {
                categorizer.processPastedContent(textarea, textarea.value);
            }
        };
        
        // Insert button after textarea
        textarea.parentNode.insertBefore(analysisBtn, textarea.nextSibling);
    });
});