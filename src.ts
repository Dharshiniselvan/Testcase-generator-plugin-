import * as vscode from 'vscode';
import axios from 'axios'; // Dev 3 must run: npm install axios

export function activate(context: vscode.ExtensionContext) {
    // 1. Register the Command
    let disposable = vscode.commands.registerCommand('extension.generateTests', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) { return; }

        // Grab the highlighted text
        const highlightedCode = editor.document.getText(editor.selection);
        
        vscode.window.showInformationMessage('Sending code to AI Judge...');

        try {
            // 2. Send code to Dev 1's Flask Server
            const response = await axios.post('http://localhost:5000/test', {
                code: highlightedCode
            });

            // 3. Update the Sidebar with Results
            const results = response.data; // This is the JSON from Dev 1 & 2
            updateWebview(results);

        } catch (error) {
            vscode.window.showErrorMessage('Failed to connect to Flask Server.');
        }
    });

    context.subscriptions.push(disposable);
}

// Function to show the results in the Sidebar
function updateWebview(data: any) {
    const panel = vscode.window.createWebviewPanel(
        'testResults',
        'Test Results',
        vscode.ViewColumn.Two,
        {}
    );

    // Simple HTML Table for the Results
    panel.webview.html = `
        <html>
            <body>
                <h2>Test Results</h2>
                <table border="1">
                    <tr><th>Input</th><th>Expected</th><th>Result</th></tr>
                    ${data.map((test: any) => `
                        <tr style="color: ${test.status === 'PASS' ? 'green' : 'red'}">
                            <td>${test.input}</td>
                            <td>${test.expected}</td>
                            <td>${test.status}</td>
                        </tr>
                    `).join('')}
                </table>
            </body>
        </html>
    `;
}