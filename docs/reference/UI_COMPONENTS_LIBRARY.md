# FAITHH UI Components Library

**Purpose:** Reusable UI patterns and components for FAITHH  
**Version:** 1.0  
**Date:** 2025-11-09

---

## 🎨 Component Philosophy

**Principles:**
- **Modular:** Each component is self-contained
- **Reusable:** Copy-paste into any page
- **Accessible:** Keyboard navigation, screen readers
- **Responsive:** Works on all screen sizes
- **Clean:** Minimal dependencies

---

## 1. Source Display Component

**Use Case:** Show RAG sources used to generate response

### HTML Structure
```html
<div class="sources-panel">
    <div class="sources-header">
        <span class="sources-icon">📚</span>
        <span class="sources-title">Sources Used</span>
        <span class="sources-count">3</span>
    </div>
    <div class="sources-list">
        <div class="source-item" data-relevance="0.92">
            <div class="source-header">
                <div class="source-name">Machine_Learning_Guide.pdf</div>
                <div class="source-score">92%</div>
            </div>
            <div class="source-snippet">
                Neural networks are computational models inspired by...
            </div>
            <div class="source-meta">
                <span>Page 15</span>
                <span>•</span>
                <span>Added 2025-01-10</span>
            </div>
        </div>
        <!-- More source items -->
    </div>
</div>
```

### CSS
```css
.sources-panel {
    background: var(--bg-light);
    border-radius: 8px;
    padding: 16px;
    margin-top: 12px;
}

.sources-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    font-weight: 600;
}

.sources-icon {
    font-size: 18px;
}

.sources-count {
    margin-left: auto;
    background: var(--primary);
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
}

.sources-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.source-item {
    background: var(--bg-medium);
    border-left: 3px solid var(--primary);
    padding: 12px;
    border-radius: 6px;
    transition: background 0.2s;
    cursor: pointer;
}

.source-item:hover {
    background: var(--bg-dark);
}

.source-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.source-name {
    font-weight: 500;
    color: var(--text-primary);
}

.source-score {
    background: var(--success);
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}

.source-snippet {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 8px;
}

.source-meta {
    font-size: 11px;
    color: var(--text-secondary);
    display: flex;
    gap: 6px;
}
```

### JavaScript
```javascript
function displaySources(sources) {
    const html = `
        <div class="sources-panel">
            <div class="sources-header">
                <span class="sources-icon">📚</span>
                <span class="sources-title">Sources Used</span>
                <span class="sources-count">${sources.length}</span>
            </div>
            <div class="sources-list">
                ${sources.map(source => `
                    <div class="source-item" data-relevance="${source.relevance}">
                        <div class="source-header">
                            <div class="source-name">${source.document}</div>
                            <div class="source-score">${Math.round(source.relevance * 100)}%</div>
                        </div>
                        <div class="source-snippet">${source.snippet}</div>
                        <div class="source-meta">
                            <span>Relevance: ${source.relevance.toFixed(2)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    return html;
}

// Usage
const sources = [
    {
        document: "ML_Guide.pdf",
        relevance: 0.92,
        snippet: "Neural networks are..."
    }
];
const sourcesHtml = displaySources(sources);
```

---

## 2. Settings Panel Component

**Use Case:** Adjust model parameters (temperature, max tokens, etc.)

### HTML Structure
```html
<div class="settings-panel">
    <div class="settings-header">
        <h3>⚙️ Settings</h3>
    </div>
    
    <div class="setting-group">
        <label class="setting-label">
            <span>Temperature</span>
            <span class="setting-value" id="temp-value">0.7</span>
        </label>
        <input type="range" class="setting-slider" 
               id="temperature" min="0" max="1" step="0.1" value="0.7">
        <div class="setting-description">
            Controls randomness. Lower = focused, Higher = creative
        </div>
    </div>
    
    <div class="setting-group">
        <label class="setting-label">
            <span>Max Tokens</span>
            <span class="setting-value" id="tokens-value">1000</span>
        </label>
        <input type="range" class="setting-slider" 
               id="max-tokens" min="100" max="2000" step="100" value="1000">
        <div class="setting-description">
            Maximum response length
        </div>
    </div>
    
    <div class="setting-group">
        <label class="setting-label">
            <span>Use RAG</span>
            <input type="checkbox" class="setting-toggle" id="use-rag" checked>
        </label>
        <div class="setting-description">
            Enable knowledge base search
        </div>
    </div>
    
    <button class="settings-save-btn">Save Settings</button>
</div>
```

### CSS
```css
.settings-panel {
    background: var(--bg-medium);
    border-radius: 12px;
    padding: 20px;
    max-width: 400px;
}

.settings-header h3 {
    margin: 0 0 20px 0;
    font-size: 18px;
}

.setting-group {
    margin-bottom: 24px;
}

.setting-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    font-weight: 500;
}

.setting-value {
    color: var(--primary);
    font-weight: 600;
}

.setting-slider {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: var(--bg-light);
    outline: none;
    -webkit-appearance: none;
}

.setting-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--primary);
    cursor: pointer;
}

.setting-toggle {
    width: 50px;
    height: 26px;
    position: relative;
    -webkit-appearance: none;
    background: var(--bg-light);
    outline: none;
    border-radius: 13px;
    cursor: pointer;
    transition: background 0.3s;
}

.setting-toggle:checked {
    background: var(--primary);
}

.setting-toggle:before {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    top: 3px;
    left: 3px;
    background: white;
    transition: left 0.3s;
}

.setting-toggle:checked:before {
    left: 27px;
}

.setting-description {
    font-size: 12px;
    color: var(--text-secondary);
    margin-top: 6px;
}

.settings-save-btn {
    width: 100%;
    padding: 12px;
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    margin-top: 12px;
}
```

### JavaScript
```javascript
class SettingsManager {
    constructor() {
        this.settings = {
            temperature: 0.7,
            maxTokens: 1000,
            useRag: true
        };
        this.init();
    }
    
    init() {
        // Temperature slider
        const tempSlider = document.getElementById('temperature');
        tempSlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            document.getElementById('temp-value').textContent = value.toFixed(1);
            this.settings.temperature = value;
        });
        
        // Max tokens slider
        const tokensSlider = document.getElementById('max-tokens');
        tokensSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            document.getElementById('tokens-value').textContent = value;
            this.settings.maxTokens = value;
        });
        
        // RAG toggle
        const ragToggle = document.getElementById('use-rag');
        ragToggle.addEventListener('change', (e) => {
            this.settings.useRag = e.target.checked;
        });
    }
    
    getSettings() {
        return this.settings;
    }
    
    saveSettings() {
        localStorage.setItem('faithh_settings', JSON.stringify(this.settings));
        console.log('Settings saved:', this.settings);
    }
    
    loadSettings() {
        const saved = localStorage.getItem('faithh_settings');
        if (saved) {
            this.settings = JSON.parse(saved);
            this.applySettings();
        }
    }
    
    applySettings() {
        document.getElementById('temperature').value = this.settings.temperature;
        document.getElementById('temp-value').textContent = this.settings.temperature.toFixed(1);
        document.getElementById('max-tokens').value = this.settings.maxTokens;
        document.getElementById('tokens-value').textContent = this.settings.maxTokens;
        document.getElementById('use-rag').checked = this.settings.useRag;
    }
}

// Usage
const settingsManager = new SettingsManager();
settingsManager.loadSettings();
```

---

## 3. Toast Notification Component

**Use Case:** Show temporary success/error/info messages

### HTML Structure
```html
<div class="toast-container" id="toast-container"></div>
```

### CSS
```css
.toast-container {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.toast {
    background: var(--bg-light);
    color: var(--text-primary);
    padding: 16px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 300px;
    animation: slideIn 0.3s ease-out;
    border-left: 4px solid var(--primary);
}

.toast.success {
    border-left-color: var(--success);
}

.toast.error {
    border-left-color: var(--danger);
}

.toast.warning {
    border-left-color: var(--warning);
}

.toast-icon {
    font-size: 20px;
}

.toast-content {
    flex: 1;
}

.toast-title {
    font-weight: 600;
    margin-bottom: 4px;
}

.toast-message {
    font-size: 13px;
    color: var(--text-secondary);
}

.toast-close {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 20px;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
}

@keyframes slideIn {
    from {
        transform: translateX(400px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOut {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(400px);
        opacity: 0;
    }
}

.toast.removing {
    animation: slideOut 0.3s ease-in;
}
```

### JavaScript
```javascript
class ToastManager {
    constructor() {
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'toast-container';
            document.body.appendChild(this.container);
        }
    }
    
    show(message, type = 'info', duration = 3000) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-icon">${icons[type]}</div>
            <div class="toast-content">
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">×</button>
        `;
        
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.onclick = () => this.remove(toast);
        
        this.container.appendChild(toast);
        
        if (duration > 0) {
            setTimeout(() => this.remove(toast), duration);
        }
        
        return toast;
    }
    
    remove(toast) {
        toast.classList.add('removing');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }
    
    success(message, duration) {
        return this.show(message, 'success', duration);
    }
    
    error(message, duration) {
        return this.show(message, 'error', duration);
    }
    
    warning(message, duration) {
        return this.show(message, 'warning', duration);
    }
    
    info(message, duration) {
        return this.show(message, 'info', duration);
    }
}

// Usage
const toast = new ToastManager();
toast.success('Message sent successfully!');
toast.error('Failed to connect to backend');
toast.warning('Backend is running in offline mode');
toast.info('Loading...', 0); // Stays until manually closed
```

---

## 4. Loading Skeleton Component

**Use Case:** Show placeholder while content loads

### HTML Structure
```html
<div class="skeleton-container">
    <div class="skeleton-line"></div>
    <div class="skeleton-line short"></div>
    <div class="skeleton-line"></div>
    <div class="skeleton-box"></div>
</div>
```

### CSS
```css
.skeleton-container {
    padding: 20px;
}

.skeleton-line,
.skeleton-box {
    background: linear-gradient(
        90deg,
        var(--bg-light) 0%,
        var(--bg-medium) 50%,
        var(--bg-light) 100%
    );
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s infinite;
    border-radius: 4px;
    margin-bottom: 12px;
}

.skeleton-line {
    height: 16px;
    width: 100%;
}

.skeleton-line.short {
    width: 60%;
}

.skeleton-box {
    height: 100px;
    width: 100%;
}

@keyframes skeleton-loading {
    0% {
        background-position: 200% 0;
    }
    100% {
        background-position: -200% 0;
    }
}
```

---

## 5. Modal Dialog Component

**Use Case:** Display settings, confirmations, or full-screen content

### HTML Structure
```html
<div class="modal-overlay" id="modal-overlay">
    <div class="modal">
        <div class="modal-header">
            <h2 class="modal-title">Modal Title</h2>
            <button class="modal-close">×</button>
        </div>
        <div class="modal-body">
            <!-- Modal content -->
        </div>
        <div class="modal-footer">
            <button class="modal-btn secondary">Cancel</button>
            <button class="modal-btn primary">Confirm</button>
        </div>
    </div>
</div>
```

### CSS
```css
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s;
}

.modal-overlay.active {
    opacity: 1;
    pointer-events: all;
}

.modal {
    background: var(--bg-medium);
    border-radius: 12px;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    display: flex;
    flex-direction: column;
    transform: scale(0.9);
    transition: transform 0.3s;
}

.modal-overlay.active .modal {
    transform: scale(1);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid var(--border);
}

.modal-title {
    margin: 0;
    font-size: 20px;
}

.modal-close {
    background: none;
    border: none;
    font-size: 28px;
    color: var(--text-secondary);
    cursor: pointer;
    width: 32px;
    height: 32px;
    padding: 0;
}

.modal-body {
    padding: 20px;
    overflow-y: auto;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 20px;
    border-top: 1px solid var(--border);
}

.modal-btn {
    padding: 10px 20px;
    border-radius: 6px;
    border: none;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}

.modal-btn.primary {
    background: var(--primary);
    color: white;
}

.modal-btn.secondary {
    background: var(--bg-light);
    color: var(--text-primary);
}
```

### JavaScript
```javascript
class Modal {
    constructor(id) {
        this.overlay = document.getElementById(id);
        this.modal = this.overlay.querySelector('.modal');
        this.closeBtn = this.overlay.querySelector('.modal-close');
        
        this.closeBtn.onclick = () => this.hide();
        this.overlay.onclick = (e) => {
            if (e.target === this.overlay) this.hide();
        };
    }
    
    show() {
        this.overlay.classList.add('active');
    }
    
    hide() {
        this.overlay.classList.remove('active');
    }
    
    setContent(title, body) {
        this.overlay.querySelector('.modal-title').textContent = title;
        this.overlay.querySelector('.modal-body').innerHTML = body;
    }
}

// Usage
const modal = new Modal('modal-overlay');
modal.setContent('Settings', '<p>Settings content here</p>');
modal.show();
```

---

## 6. Code Block Component

**Use Case:** Display formatted code in responses

### HTML + CSS
```html
<style>
.code-block {
    background: var(--bg-dark);
    border-radius: 8px;
    overflow: hidden;
    margin: 12px 0;
    border: 1px solid var(--border);
}

.code-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 12px;
    background: var(--bg-medium);
    border-bottom: 1px solid var(--border);
}

.code-language {
    font-size: 12px;
    color: var(--text-secondary);
    text-transform: uppercase;
}

.code-copy-btn {
    background: var(--bg-light);
    border: none;
    color: var(--text-primary);
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
}

.code-content {
    padding: 16px;
    overflow-x: auto;
}

.code-content code {
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-primary);
}
</style>

<div class="code-block">
    <div class="code-header">
        <span class="code-language">python</span>
        <button class="code-copy-btn" onclick="copyCode(this)">Copy</button>
    </div>
    <div class="code-content">
        <code>def hello_world():
    print("Hello, FAITHH!")</code>
    </div>
</div>

<script>
function copyCode(btn) {
    const codeBlock = btn.closest('.code-block');
    const code = codeBlock.querySelector('code').textContent;
    navigator.clipboard.writeText(code);
    btn.textContent = 'Copied!';
    setTimeout(() => btn.textContent = 'Copy', 2000);
}
</script>
```

---

## 🎯 Usage Examples

### Integrate Source Display
```javascript
// After getting response from backend
if (response.sources && response.sources.length > 0) {
    const sourcesHtml = displaySources(response.sources);
    messageContent.innerHTML += sourcesHtml;
}
```

### Show Toast on Error
```javascript
try {
    const response = await fetch(url);
    // ...
} catch (error) {
    toast.error('Failed to connect to backend');
}
```

### Display Loading Skeleton
```javascript
// Before API call
messagesContainer.innerHTML += `
    <div class="skeleton-container" id="loading">
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
    </div>
`;

// After API call
document.getElementById('loading').remove();
```

---

## 📱 Responsive Patterns

### Mobile-First Breakpoints
```css
/* Mobile first */
.component {
    /* Mobile styles */
}

/* Tablet */
@media (min-width: 768px) {
    .component {
        /* Tablet styles */
    }
}

/* Desktop */
@media (min-width: 1024px) {
    .component {
        /* Desktop styles */
    }
}
```

---

## 🎨 Color Scheme Templates

### Dark Theme (Current)
```css
:root {
    --primary: #2563eb;
    --bg-dark: #0f172a;
    --bg-medium: #1e293b;
    --bg-light: #334155;
    --text-primary: #f1f5f9;
}
```

### Light Theme Alternative
```css
:root {
    --primary: #2563eb;
    --bg-dark: #ffffff;
    --bg-medium: #f8fafc;
    --bg-light: #f1f5f9;
    --text-primary: #0f172a;
}
```

---

## 🚀 Next Steps

1. **Copy components as needed** into your UI
2. **Customize colors** to match your brand
3. **Test responsiveness** on mobile
4. **Add accessibility** features (ARIA labels, keyboard nav)

---

*Component library for FAITHH UI v4+*  
*Created: 2025-11-09*
