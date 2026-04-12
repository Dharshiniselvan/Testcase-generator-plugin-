import json
import sys
import urllib.request
import urllib.error
import re

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.3-70b-versatile"

def extract_all_functions(code):
    """Extract all functions from code as separate strings."""
    lines = code.split('\n')
    functions = []
    current_func = []
    inside_func = False

    for line in lines:
        if line.startswith('def '):
            if current_func:
                functions.append('\n'.join(current_func))
            current_func = [line]
            inside_func = True
        elif inside_func:
            current_func.append(line)

    if current_func:
        functions.append('\n'.join(current_func))

    return functions

def extract_script_part(code):
    """Extract script part (before first def) that has input() calls."""
    lines = code.split('\n')
    script_lines = []
    for line in lines:
        if line.startswith('def '):
            break
        script_lines.append(line)
    script = '\n'.join(script_lines).strip()
    # Only return if it has input() calls
    if 'input(' in script:
        return script
    return None

def has_function(code):
    return bool(re.search(r"def\s+(\w+)\s*\(", code))

def clean_json(text):
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            if part.startswith("json"):
                part = part[4:]
            part = part.strip()
            if part.startswith("{"):
                text = part
                break

    start = text.find("{")
    if start == -1:
        return text

    count = 0
    end = -1
    for i in range(start, len(text)):
        if text[i] == '{':
            count += 1
        elif text[i] == '}':
            count -= 1
            if count == 0:
                end = i
                break

    if end != -1:
        text = text[start:end+1]

    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)
    return text

def call_groq(prompt, api_key):
    try:
        payload = json.dumps({
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "max_tokens": 1000
        }).encode("utf-8")

        req = urllib.request.Request(GROQ_URL, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", "Bearer " + api_key)
        req.add_header("User-Agent", "Mozilla/5.0")
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
            text = result["choices"][0]["message"]["content"].strip()

        cleaned = clean_json(text)
        parsed = json.loads(cleaned)
        if "complexity" not in parsed:
            parsed["complexity"] = "O(n)"
        return parsed

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return {"error": f"HTTP {e.code}: {body}"}
    except Exception as e:
        return {"error": str(e)}

def generate_testcases_for_function(func_code, api_key):
    prompt = f"""You are a Python testing expert. Analyze this function carefully and generate exactly 5 test cases.

RULES FOR "input" field:
- "input" is always a JSON array
- Each element corresponds to one parameter IN ORDER
- List param: [[1,2,3]]
- Int param: [5]
- String param: ["hello"]
- Bool param: [true]
- Two params (a,b): [a_value, b_value]
- List + int params (arr, key): [[1,2,3], 2]

RULES FOR "expected" field:
- Exact return value of the function
- Boolean: true/false (lowercase)
- None return: null

Return ONLY this JSON, nothing else:
{{"testcases":[{{"input":[...],"expected":...}}],"complexity":"O(?)"}}

Function:
{func_code}"""

    return call_groq(prompt, api_key)

def generate_testcases_for_script(script_code, api_key):
    prompt = f"""Analyze this Python script and generate exactly 5 test cases.
The script uses input() to get values from user.
Return ONLY valid JSON, no explanation, no markdown, no extra text.
Format: {{"testcases":[{{"input":"9001","expected":"Found (Linear Search)"}},{{"input":"9999","expected":"Not Found"}}],"complexity":"O(n)"}}

Script:
{script_code}"""

    return call_groq(prompt, api_key)

def generate_testcases(code, api_key):
    result = {}

    # Check for script part (before functions with input() calls)
    script_part = extract_script_part(code)
    if script_part:
        script_result = generate_testcases_for_script(script_part, api_key)
        result["script"] = {
            "testcases": script_result.get("testcases", []),
            "complexity": script_result.get("complexity", "O(n)")
        }

    # Check for functions
    if has_function(code):
        functions = extract_all_functions(code)
        func_results = []
        for func in functions:
            match = re.search(r"def\s+(\w+)\s*\(", func)
            func_name = match.group(1) if match else "unknown"
            res = generate_testcases_for_function(func, api_key)
            func_results.append({
                "function": func_name,
                "testcases": res.get("testcases", []),
                "complexity": res.get("complexity", "O(n)"),
                "error": res.get("error")
            })
        result["functions"] = func_results

    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No API key provided"}))
        sys.exit(1)

    api_key = sys.argv[1]
    code = sys.stdin.read()

    if code.strip():
        result = generate_testcases(code, api_key)
        print(json.dumps(result))
    else:
        print(json.dumps({"error": "No code received"}))