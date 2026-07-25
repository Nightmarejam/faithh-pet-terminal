import * as vscode from 'vscode';
import { FaithhChatViewProvider } from './FaithhChatViewProvider';
import { BackendClient } from './backendClient';

export function activate(context: vscode.ExtensionContext) {
    console.log('FAITHH extension activating...');

    const config = vscode.workspace.getConfiguration('faithh');
    const backendUrl = config.get<string>('backendUrl', 'http://localhost:5557');
    const client = new BackendClient(backendUrl);

    // Register the webview sidebar provider
    const chatProvider = new FaithhChatViewProvider(context.extensionUri, client, context);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('faithh.chatView', chatProvider, {
            webviewOptions: { retainContextWhenHidden: true }
        })
    );

    // Command: Open Chat (focus the sidebar)
    context.subscriptions.push(
        vscode.commands.registerCommand('faithh.openChat', () => {
            vscode.commands.executeCommand('faithh.chatView.focus');
        })
    );

    // Command: New Chat
    context.subscriptions.push(
        vscode.commands.registerCommand('faithh.newChat', () => {
            chatProvider.postMessageToWebview({ type: 'newChat' });
        })
    );

    // Command: Ask About This File
    context.subscriptions.push(
        vscode.commands.registerCommand('faithh.askAboutFile', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showInformationMessage('No active file to ask about.');
                return;
            }

            const fileName = editor.document.fileName;
            const selection = editor.selection;
            let context_text = '';

            if (!selection.isEmpty) {
                context_text = editor.document.getText(selection);
            } else {
                // Send first 200 lines if no selection
                const endLine = Math.min(editor.document.lineCount, 200);
                context_text = editor.document.getText(
                    new vscode.Range(0, 0, endLine, 0)
                );
            }

            const question = await vscode.window.showInputBox({
                prompt: `Ask FAITHH about ${fileName.split('/').pop()}`,
                placeHolder: 'What does this code do?'
            });

            if (question) {
                const fullMessage = `[File: ${fileName}]\n\`\`\`\n${context_text.substring(0, 3000)}\n\`\`\`\n\n${question}`;
                chatProvider.postMessageToWebview({
                    type: 'sendMessage',
                    message: fullMessage
                });
                // Focus the chat panel
                vscode.commands.executeCommand('faithh.chatView.focus');
            }
        })
    );

    // Status bar item
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.text = '$(comment-discussion) FAITHH';
    statusBar.tooltip = 'Open FAITHH Chat';
    statusBar.command = 'faithh.openChat';
    statusBar.show();
    context.subscriptions.push(statusBar);

    // Mood emoji map for PULSE avatar state
    const moodEmoji: Record<string, string> = {
        calm: '😌',
        curious: '🤔',
        excited: '✨',
        concerned: '😟',
        alert: '⚠️',
    };

    async function updatePulseStatus() {
        try {
            const pulse = await client.getPulseState();
            if (pulse.success && pulse.avatar) {
                const emoji = moodEmoji[pulse.avatar.mood] || '💬';
                const alerts = pulse.avatar.alert_count;
                statusBar.text = `$(comment-discussion) FAITHH ${emoji}${alerts > 0 ? ` (${alerts})` : ''}`;
                statusBar.color = pulse.avatar.mood === 'alert' ? '#ff6666' :
                                  pulse.avatar.mood === 'concerned' ? '#ffcc00' : '#00ffcc';
                statusBar.tooltip = `FAITHH — Mood: ${pulse.avatar.mood}, Energy: ${pulse.avatar.energy}\n` +
                    (pulse.avatar.alerts.length > 0 ? `Alerts: ${pulse.avatar.alerts.join(', ')}` : 'All systems healthy');
            }
        } catch {
            // Fall back to simple health check
        }
    }

    // Check backend connection + PULSE state
    client.checkHealth().then(ok => {
        if (ok) {
            statusBar.text = '$(comment-discussion) FAITHH ●';
            statusBar.color = '#00ffcc';
            updatePulseStatus();
        } else {
            statusBar.text = '$(comment-discussion) FAITHH ○';
            statusBar.color = '#ff6666';
            vscode.window.showWarningMessage(
                `FAITHH backend not reachable at ${backendUrl}. Start it with: cd ~/ai-stack && ./restart_backend.sh`
            );
        }
    });

    // Poll PULSE state every 5 minutes
    const pulseInterval = setInterval(updatePulseStatus, 5 * 60 * 1000);
    context.subscriptions.push({ dispose: () => clearInterval(pulseInterval) });

    console.log('FAITHH extension activated.');
}

export function deactivate() {
    console.log('FAITHH extension deactivated.');
}
