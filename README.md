# Test Case Generator Plugin for VS Code

A VS Code extension that automatically generates and validates test cases for Python code using AI.

---

## 👥 Team Members
- Archanamani S.A
- Dharshini S
- Jananisree P
- Krishna Gopeka R

---

## 📌 Features
- ✅ Automatically generates 5 test cases per function using AI
- ✅ Runs code and shows Pass/Fail results
- ✅ Handles pure function files
- ✅ Handles pure script files (with input())
- ✅ Handles mixed files (script + functions)
- ✅ Detects all function types automatically
- ✅ Timeout protection against infinite loops
- ✅ Each user has their own API key (no quota sharing)
- ✅ Two modes: Generate Only / Generate + Validate

---

## 🛠️ Requirements
- VS Code 1.90+
- Python 3.x
- Internet connection (for Groq API)
- Free Groq API key from https://console.groq.com

---

## 📦 Installation

### Step 1 — Install the VSIX extension
- Open VS Code
- Go to Extensions panel (Ctrl+Shift+X)
- Click `...` → Install from VSIX
- Select `ai-code-tester-0.0.1.vsix`

### Step 2 — Get Groq API Key (Free)
1. Go to https://console.groq.com
2. Sign up for free
3. Click API Keys → Create API Key
4. Copy the key (starts with gsk_...)

---

## 🚀 How to Use

### Step 1 — Open any Python file in VS Code

### Step 2 — Run the extension
- Press `Ctrl+Shift+P`
- Type **"Run AI Test Cases"**
- Press Enter

### Step 3 — Enter API Key (First time only)
- Paste your Groq API key
- It will be saved automatically for future use

### Step 4 — Choose what to do
```
💡 Generate Test Cases Only   → Shows AI-generated test cases
▶️  Generate + Run + Pass/Fail → Runs code and shows results
```

### Step 5 — View Results
```
=== AI TEST RESULTS ===

⚙️ FUNCTION: bubble_sort
========================================
Test 1  ✅ PASS
  Input:    [[5,3,1]]
  Expected: [1,3,5]
  Actual:   [1,3,5]
  Remarks:  Matches expected output

📝 SCRIPT PART (run manually)
========================================
Test 1  ⚠️ INFO
  Input:    "101"
  Expected: "Student Found"
```

---

## 📁 Project Structure
```
extension/
├── ai_service.py      → Calls Groq AI to generate test cases
├── judge_service.py   → Executes code and validates results
├── runner.py          → Connects AI + Judge together
├── src.ts             → VS Code extension logic
├── package.json       → Extension configuration
├── tsconfig.json      → TypeScript configuration
└── dist/
    └── src.js         → Compiled extension
```

---

## 🔄 How It Works
```
User opens Python file
        ↓
Extension reads the code
        ↓
Sends to Groq AI (generates 5 test cases per function)
        ↓
Judge runs each test case
        ↓
Shows Pass/Fail results in VS Code popup
```

---

## ⚙️ Supported File Types

| File Type | Test Cases | Validation |
|-----------|-----------|------------|
| Function file | ✅ 5 per function | ✅ Pass/Fail |
| Script file | ✅ 5 sample inputs | ⚠️ Manual only |
| Mixed file | ✅ Both | ✅ Functions validated |

---

## 🔑 API Key Management
- First run → prompts for API key
- Key saved permanently in VS Code settings
- To change key: `Ctrl+Shift+P` → "AI Tester: Set Groq API Key"
- Each user gets 14,400 free requests/day

---

## ❗ Troubleshooting

| Error | Solution |
|-------|---------|
| API key invalid | Get new key from console.groq.com |
| No output | Check Python is installed |
| Timeout error | Code has infinite loop |
| JSON parse error | Try running again |

---

## 🔗 Links
- GitHub: https://github.com/your-username/ai-code-tester

---

## 📝 License
MIT License — Free to use and modify
