import traceback
import re
import sys
import threading
import io

class TimeoutError(Exception):
    pass

def run_with_timeout(func, timeout=5):
    result_box = [None]
    error_box = [None]

    def target():
        try:
            result_box[0] = func()
        except Exception as e:
            error_box[0] = e

    t = threading.Thread(target=target)
    t.daemon = True
    t.start()
    t.join(timeout)
    if t.is_alive():
        raise TimeoutError("Execution timed out (> 5s)")
    if error_box[0]:
        raise error_box[0]
    return result_box[0]

def execute_user_code(user_code_str, func_name, inputs):
    namespace = {}
    try:
        # Check syntax
        try:
            compile(user_code_str, "<string>", "exec")
        except SyntaxError as e:
            return {"output": None, "error": f"SyntaxError: {e}"}

        # FIX: Mock input() so script part doesn't block
        namespace['input'] = lambda prompt="": "0"
        
        # Suppress stdout during exec so prints don't pollute output
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            exec(user_code_str, namespace)
        finally:
            sys.stdout = old_stdout

        if func_name not in namespace:
            return {"output": None, "error": f"Function '{func_name}' not found."}

        func = namespace[func_name]

        # Smart input unpacking
        if isinstance(inputs, list):
            if len(inputs) == 1 and isinstance(inputs[0], list):
                call = lambda: func(inputs[0])
            else:
                try:
                    call = lambda: func(*inputs)
                except TypeError:
                    call = lambda: func(inputs)
        else:
            call = lambda: func(inputs)

        try:
            actual = run_with_timeout(call, timeout=5)
        except TimeoutError as e:
            return {"output": None, "error": str(e)}

        if actual is None:
            return {"output": "None", "error": None}

        return {"output": actual, "error": None}

    except Exception:
        return {"output": None, "error": traceback.format_exc().splitlines()[-1]}

def run_judge(user_code, test_cases, func_name=None):
    if not func_name:
        match = re.search(r"def\s+(\w+)\s*\(", user_code)
        func_name = match.group(1) if match else None

    if not func_name:
        return [{"status": "ERROR", "remarks": "No function definition found."}]

    final_results = []
    for case in test_cases:
        test_input = case.get("input") or case.get("inputs")
        expected = case.get("expected")

        run_info = execute_user_code(user_code, func_name, test_input)

        if run_info["error"]:
            status = "ERROR"
            remarks = run_info["error"]
        elif run_info["output"] == expected:
            status = "PASS"
            remarks = "Matches expected output"
        elif str(run_info["output"]) == str(expected):
            status = "PASS"
            remarks = "Matches expected output"
        else:
            status = "FAIL"
            remarks = f"Expected {expected}, but got {run_info['output']}"

        final_results.append({
            "input": test_input,
            "expected": expected,
            "actual": run_info["output"] if not run_info["error"] else "N/A",
            "status": status,
            "remarks": remarks
        })

    return final_results