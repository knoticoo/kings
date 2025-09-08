/**
 * Discord Text Formatter
 * 
 * Simple formatter that converts Discord markdown to HTML
 * Focuses on tier lists and basic formatting
 */

class DiscordFormatter {
    constructor() {
        this.init();
    }

    init() {
        // Find all content textareas
        const contentTextareas = document.querySelectorAll('textarea[name="content"]');
        
        contentTextareas.forEach(textarea => {
            // Add paste event listener
            textarea.addEventListener('paste', (e) => {
                setTimeout(() => {
                    const pastedContent = e.clipboardData.getData('text/html') || e.clipboardData.getData('text/plain');
                    if (pastedContent) {
                        this.formatAndUpdate(textarea, pastedContent);
                    }
                }, 100);
            });
            
            // Add format button
            this.addFormatButton(textarea);
        });
    }

    addFormatButton(textarea) {
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'mt-2';
        
        const formatBtn = document.createElement('button');
        formatBtn.type = 'button';
        formatBtn.className = 'btn btn-sm btn-outline-success';
        formatBtn.innerHTML = '<i class="bi bi-magic me-1"></i>Format Discord Text';
        formatBtn.onclick = () => this.formatAndUpdate(textarea, textarea.value);
        
        buttonContainer.appendChild(formatBtn);
        textarea.parentNode.insertBefore(buttonContainer, textarea.nextSibling);
    }

    formatAndUpdate(textarea, content) {
        const formattedContent = this.formatDiscordText(content);
        
        if (formattedContent !== content) {
            textarea.value = formattedContent;
            this.showMessage('Discord text has been automatically formatted!', 'success');
        } else {
            this.showMessage('No formatting changes needed.', 'info');
        }
    }

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

// Initialize the formatter when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new DiscordFormatter();
});