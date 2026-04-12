import * as vscode from 'vscode';
import { spawn } from 'child_process';
import * as path from 'path';

const KEY_STORAGE = 'groqApiKey';

function runPython(scriptPath: string, code: string, apiKey: string): Promise<string> {
    return new Promise((resolve, reject) => {
        const py = spawn('python', [scriptPath, apiKey]);
        let output = "";
        let errorOutput = "";

        py.stdout.on('data', (data: Buffer) => { output += data.toString(); });
        py.stderr.on('data', (data: Buffer) => { errorOutput += data.toString(); });

        py.on('close', () => {
            if (!output.trim()) {
                reject(errorOutput || "No output from Python");
            } else {
                resolve(output.trim());
            }
        });

        py.stdin.write(code);
        py.stdin.end();
    });
}

export function activate(context: vscode.ExtensionContext) {

    context.subscriptions.push(
        vscode.commands.registerCommand('aiTester.setKey', async () => {
            const key = await vscode.window.showInputBox({
                prompt: "Enter your Groq API key",
                password: true,
                placeHolder: "gsk_..."
            });
            if (key) {
                await context.globalState.update(KEY_STORAGE, key);
                vscode.window.showInformationMessage("✅ Groq API key saved!");
            }
        })
    );

    let disposable = vscode.commands.registerCommand('aiTester.run', async () => {

        // Step 1: Get API key
        let apiKey = context.globalState.get<string>(KEY_STORAGE);
        if (!apiKey) {
            apiKey = await vscode.window.showInputBox({
                prompt: "Enter your Groq API key (free at https://console.groq.com)",
                password: true,
                placeHolder: "gsk_..."
            });
            if (!apiKey) {
                vscode.window.showErrorMessage("API key is required!");
                return;
            }
            await context.globalState.update(KEY_STORAGE, apiKey);
            vscode.window.showInformationMessage("✅ API key saved!");
        }

        // Step 2: Get current open file
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage("No file is open");
            return;
        }

        const code = editor.document.getText();
        if (!code.trim()) {
            vscode.window.showErrorMessage("The file is empty.");
            return;
        }

        // Step 3: Ask user what they want
        const choice = await vscode.window.showQuickPick(
            [
                { label: "$(lightbulb) Generate Test Cases Only", description: "Show AI-generated test cases", value: "testcases" },
                { label: "$(play) Generate + Run + Pass/Fail", description: "Run code and show Pass/Fail results", value: "judge" }
            ],
            { placeHolder: "What do you want to do?" }
        );

        if (!choice) return;

        vscode.window.showInformationMessage("Running AI analysis...");

        const basePath = path.join(__dirname, '..');

        try {
            if (choice.value === "testcases") {
                const aiServicePath = path.join(basePath, 'ai_service.py');
                const output = await runPython(aiServicePath, code, apiKey);
                const result = JSON.parse(output);

                if (result.error) {
                    vscode.window.showErrorMessage(`AI Error: ${result.error}`);
                    return;
                }

                let message = "=== AI TEST CASES ===\n";

                // Script part
                if (result.script && result.script.testcases && result.script.testcases.length > 0) {
                    message += "\n📝 SCRIPT PART (sample inputs)\n";
                    message += "=".repeat(40) + "\n\n";
                    result.script.testcases.forEach((t: any, i: number) => {
                        message += `Test ${i + 1}\n`;
                        message += `  Input:    ${JSON.stringify(t.input)}\n`;
                        message += `  Expected: ${JSON.stringify(t.expected)}\n\n`;
                    });
                    message += `Complexity: ${result.script.complexity}\n`;
                }

                // Functions part
                if (result.functions && result.functions.length > 0) {
                    result.functions.forEach((f: any) => {
                        message += `\n⚙️ FUNCTION: ${f.function}\n`;
                        message += "=".repeat(40) + "\n\n";
                        if (f.testcases && f.testcases.length > 0) {
                            f.testcases.forEach((t: any, i: number) => {
                                message += `Test ${i + 1}\n`;
                                message += `  Input:    ${JSON.stringify(t.input)}\n`;
                                message += `  Expected: ${JSON.stringify(t.expected)}\n\n`;
                            });
                        }
                        message += `Complexity: ${f.complexity}\n`;
                    });
                }

                vscode.window.showInformationMessage(message, { modal: true });

            } else {
                const runnerPath = path.join(basePath, 'runner.py');
                const output = await runPython(runnerPath, code, apiKey);
                const result = JSON.parse(output);

                if (result.error) {
                    vscode.window.showErrorMessage(`Error: ${result.error}`);
                    return;
                }

                let message = "=== AI TEST RESULTS ===\n";

                // Script part
                if (result.script && result.script.results && result.script.results.length > 0) {
                    message += "\n📝 SCRIPT PART (run manually)\n";
                    message += "=".repeat(40) + "\n\n";
                    result.script.results.forEach((t: any, i: number) => {
                        message += `Test ${i + 1}  ⚠️ INFO\n`;
                        message += `  Input:    ${JSON.stringify(t.input)}\n`;
                        message += `  Expected: ${JSON.stringify(t.expected)}\n`;
                        message += `  Remarks:  ${t.remarks}\n\n`;
                    });
                    message += `Complexity: ${result.script.complexity}\n`;
                }

                // Functions part
                if (result.functions && result.functions.length > 0) {
                    result.functions.forEach((f: any) => {
                        message += `\n⚙️ FUNCTION: ${f.function}\n`;
                        message += "=".repeat(40) + "\n\n";
                        if (f.results && f.results.length > 0) {
                            f.results.forEach((t: any, i: number) => {
                                const icon = t.status === "PASS" ? "✅" : t.status === "FAIL" ? "❌" : "⚠️";
                                message += `Test ${i + 1}  ${icon} ${t.status}\n`;
                                if (t.input !== undefined) message += `  Input:    ${JSON.stringify(t.input)}\n`;
                                if (t.expected !== undefined) message += `  Expected: ${JSON.stringify(t.expected)}\n`;
                                if (t.actual !== undefined) message += `  Actual:   ${JSON.stringify(t.actual)}\n`;
                                message += `  Remarks:  ${t.remarks}\n\n`;
                            });
                        }
                        message += `Complexity: ${f.complexity}\n`;
                    });
                }

                vscode.window.showInformationMessage(message, { modal: true });
            }

        } catch (err: any) {
            vscode.window.showErrorMessage(`Error: ${err.message || err}`);
        }
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}