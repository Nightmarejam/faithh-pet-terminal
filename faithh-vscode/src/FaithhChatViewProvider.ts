import * as vscode from 'vscode';
import { BackendClient } from './backendClient';

export class FaithhChatViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'faithh.chatView';
    private _view?: vscode.WebviewView;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly _client: BackendClient,
        private readonly _context: vscode.ExtensionContext
    ) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        _context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlContent(webviewView.webview);

        // Handle messages from the webview
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'chat': {
                    try {
                        // Optionally attach file context
                        let fullMessage = message.text;
                        const config = vscode.workspace.getConfiguration('faithh');
                        if (config.get<boolean>('sendFileContext', true)) {
                            const editor = vscode.window.activeTextEditor;
                            if (editor) {
                                const fileName = editor.document.fileName;
                                const lineCount = editor.document.lineCount;
                                fullMessage = `[Active file: ${fileName} (${lineCount} lines)]\n${message.text}`;
                            }
                        }

                        const configModel = config.get<string>('defaultModel', '');
                        const response = await this._client.chat(
                            fullMessage,
                            message.model || configModel || '',
                            message.useRag !== false
                        );

                        webviewView.webview.postMessage({
                            type: 'chatResponse',
                            data: response
                        });
                    } catch (err: unknown) {
                        const errorMsg = err instanceof Error ? err.message : 'Unknown error';
                        webviewView.webview.postMessage({
                            type: 'chatError',
                            error: errorMsg
                        });
                    }
                    break;
                }
                case 'openFile': {
                    if (message.path) {
                        const doc = await vscode.workspace.openTextDocument(message.path);
                        await vscode.window.showTextDocument(doc);
                    }
                    break;
                }
                case 'copyToClipboard': {
                    await vscode.env.clipboard.writeText(message.text);
                    vscode.window.showInformationMessage('Copied to clipboard');
                    break;
                }
                case 'insertAtCursor': {
                    const editor = vscode.window.activeTextEditor;
                    if (editor) {
                        await editor.edit(editBuilder => {
                            editBuilder.insert(editor.selection.active, message.text);
                        });
                    }
                    break;
                }
            }
        });
    }

    public postMessageToWebview(message: { type: string; message?: string }) {
        if (this._view) {
            this._view.webview.postMessage(message);
        }
    }

    private _getHtmlContent(webview: vscode.Webview): string {
        const nonce = getNonce();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-${nonce}'; connect-src http://localhost:* https://*;">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
            color: var(--vscode-foreground);
            background: var(--vscode-sideBar-background);
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 12px;
            border-bottom: 1px solid var(--vscode-panel-border);
            background: var(--vscode-sideBarSectionHeader-background);
        }

        .header-title {
            font-weight: bold;
            color: var(--vscode-sideBarTitle-foreground);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #555;
        }
        .status-dot.online { background: #00cc88; }
        .status-dot.offline { background: #ff4444; }

        .new-chat-btn {
            background: none;
            border: 1px solid var(--vscode-button-border, var(--vscode-panel-border));
            color: var(--vscode-button-foreground);
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 3px;
            cursor: pointer;
        }
        .new-chat-btn:hover {
            background: var(--vscode-button-hoverBackground);
        }

        .chat-display {
            flex: 1;
            overflow-y: auto;
            padding: 8px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .message {
            padding: 8px 10px;
            border-radius: 6px;
            font-size: 12px;
            line-height: 1.5;
        }
        .message.user {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            align-self: flex-end;
            max-width: 90%;
        }
        .message.assistant {
            background: var(--vscode-editor-background);
            border: 1px solid var(--vscode-panel-border);
        }
        .message .role {
            font-size: 10px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 4px;
            color: var(--vscode-descriptionForeground);
        }
        .message.user .role { color: #4fc1ff; }
        .message.assistant .role { color: #00cc88; }

        .message pre {
            background: var(--vscode-textCodeBlock-background);
            padding: 6px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 4px 0;
        }
        .message code {
            font-family: var(--vscode-editor-font-family);
            font-size: 11px;
        }

        .message-actions {
            display: flex;
            gap: 6px;
            margin-top: 6px;
        }
        .message-actions button {
            background: none;
            border: none;
            color: var(--vscode-descriptionForeground);
            font-size: 10px;
            cursor: pointer;
            padding: 2px 4px;
        }
        .message-actions button:hover {
            color: var(--vscode-foreground);
        }

        .input-area {
            padding: 8px;
            border-top: 1px solid var(--vscode-panel-border);
            display: flex;
            gap: 6px;
        }

        .input-area textarea {
            flex: 1;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            padding: 6px 8px;
            font-family: var(--vscode-font-family);
            font-size: 12px;
            resize: none;
            min-height: 32px;
            max-height: 120px;
        }
        .input-area textarea:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }

        .send-btn {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 12px;
            align-self: flex-end;
        }
        .send-btn:hover { background: var(--vscode-button-hoverBackground); }
        .send-btn:disabled { opacity: 0.5; cursor: not-allowed; }

        .typing-indicator {
            display: inline-flex;
            gap: 3px;
            padding: 4px 0;
        }
        .typing-indicator span {
            width: 6px; height: 6px;
            background: var(--vscode-descriptionForeground);
            border-radius: 50%;
            animation: bounce 1.2s infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-4px); }
        }
    </style>
</head>
<body>
    <div class="header">
        <div style="display:flex;align-items:center;gap:6px;">
            <div class="status-dot" id="statusDot"></div>
            <span class="header-title">FAITHH</span>
        </div>
        <button class="new-chat-btn" id="newChatBtn">+ New</button>
    </div>

    <div class="chat-display" id="chatDisplay">
        <div class="message assistant">
            <div class="role">FAITHH</div>
            <div>Ready. How can I help?</div>
        </div>
    </div>

    <div class="input-area">
        <textarea id="chatInput" placeholder="Ask FAITHH..." rows="1"></textarea>
        <button class="send-btn" id="sendBtn">Send</button>
    </div>

    <script nonce="${nonce}">
        const vscode = acquireVsCodeApi();
        const chatDisplay = document.getElementById('chatDisplay');
        const chatInput = document.getElementById('chatInput');
        const sendBtn = document.getElementById('sendBtn');
        const statusDot = document.getElementById('statusDot');

        // Auto-resize textarea
        chatInput.addEventListener('input', () => {
            chatInput.style.height = 'auto';
            chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
        });

        // Send button click
        sendBtn.addEventListener('click', () => sendMessage());

        // Enter to send (Shift+Enter for newline)
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // New chat button
        document.getElementById('newChatBtn').addEventListener('click', () => newChat());

        function sendMessage() {
            const text = chatInput.value.trim();
            if (!text) return;

            // Show user message
            addMessage('user', text);
            chatInput.value = '';
            chatInput.style.height = 'auto';

            // Show typing indicator
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message assistant';
            typingDiv.id = 'typing';
            typingDiv.innerHTML = '<div class="role">FAITHH</div><div class="typing-indicator"><span></span><span></span><span></span></div>';
            chatDisplay.appendChild(typingDiv);
            chatDisplay.scrollTop = chatDisplay.scrollHeight;

            sendBtn.disabled = true;

            // Send to extension host → backend
            vscode.postMessage({ type: 'chat', text: text });
        }

        function addMessage(role, content, isHtml) {
            const div = document.createElement('div');
            div.className = 'message ' + (role === 'user' ? 'user' : 'assistant');
            const roleLabel = role === 'user' ? 'YOU' : 'FAITHH';
            div.innerHTML = '<div class="role">' + roleLabel + '</div><div>' + (isHtml ? content : escapeHtml(content)) + '</div>';

            if (role === 'assistant') {
                const actions = document.createElement('div');
                actions.className = 'message-actions';
                const copyBtn = document.createElement('button');
                copyBtn.textContent = 'Copy';
                copyBtn.addEventListener('click', () => {
                    const content = div.querySelector('div:nth-child(2)').textContent;
                    vscode.postMessage({ type: 'copyToClipboard', text: content });
                });
                const insertBtn = document.createElement('button');
                insertBtn.textContent = 'Insert at cursor';
                insertBtn.addEventListener('click', () => {
                    const content = div.querySelector('div:nth-child(2)').textContent;
                    vscode.postMessage({ type: 'insertAtCursor', text: content });
                });
                actions.appendChild(copyBtn);
                actions.appendChild(insertBtn);
                div.appendChild(actions);
            }

            chatDisplay.appendChild(div);
            chatDisplay.scrollTop = chatDisplay.scrollHeight;
        }

        function newChat() {
            chatDisplay.innerHTML = '<div class="message assistant"><div class="role">FAITHH</div><div>New chat. Ready.</div></div>';
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Handle messages from extension host
        window.addEventListener('message', event => {
            const msg = event.data;
            // Remove typing indicator
            const typing = document.getElementById('typing');
            if (typing) typing.remove();
            sendBtn.disabled = false;

            switch (msg.type) {
                case 'chatResponse':
                    if (msg.data && msg.data.response) {
                        addMessage('assistant', msg.data.response, true);
                    }
                    statusDot.className = 'status-dot online';
                    break;
                case 'chatError':
                    addMessage('assistant', 'Error: ' + (msg.error || 'Connection failed'));
                    statusDot.className = 'status-dot offline';
                    break;
                case 'newChat':
                    newChat();
                    break;
                case 'sendMessage':
                    if (msg.message) {
                        chatInput.value = msg.message;
                        sendMessage();
                    }
                    break;
            }
        });

        // Initial status check
        statusDot.className = 'status-dot online';
    </script>
</body>
</html>`;
    }
}

function getNonce(): string {
    let text = '';
    const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    for (let i = 0; i < 32; i++) {
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    }
    return text;
}
