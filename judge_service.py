import traceback

def execute_user_code(user_code_str, func_name, inputs):
    namespace = {}
    try:
        exec(user_code_str, namespace)
        if func_name not in namespace:
            return {"output": None, "error": f"Function '{func_name}' not found."}
        
        func = namespace[func_name]
        # Handle unpacking inputs
        actual = func(*inputs) if isinstance(inputs, list) else func(inputs)
        return {"output": actual, "error": None}
    except Exception:
        return {"output": None, "error": traceback.format_exc().splitlines()[-1]}

def run_judge(user_code, test_cases):
    """
    This is the function the Flask server will call.
    user_code: String from Developer 3 (VS Code)
    test_cases: List from Developer 1 (AI)
    """
    # Auto-find function name (Basic version: first 'def')
    import re
    match = re.search(r"def\s+(\w+)\s*\(", user_code)
    func_name = match.group(1) if match else None

    if not func_name:
        return [{"status": "ERROR", "remarks": "No function definition found."}]

    final_results = []
    for case in test_cases:
        # Compatibility check: handle 'input' or 'inputs' keys
        test_input = case.get("input") or case.get("inputs")
        expected = case.get("expected")
        
        run_info = execute_user_code(user_code, func_name, test_input)
        
        if run_info["error"]:
            status, remarks = "ERROR", run_info["error"]
        elif run_info["output"] == expected:
            status, remarks = "PASS", "Matches expected output"
        else:
            status, remarks = "FAIL", f"Expected {expected}, but got {run_info['output']}"
            
        final_results.append({
            "input": test_input,
            "expected": expected,
            "actual": run_info["output"] if not run_info["error"] else "N/A",
            "status": status,
            "remarks": remarks
        })
    return final_results