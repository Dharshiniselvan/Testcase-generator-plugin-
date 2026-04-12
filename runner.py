import json
import sys
import os
import re

# Redirect stderr to suppress unwanted prints from user code
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ai_service
import judge_service

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No API key provided"}))
        sys.exit(1)

    api_key = sys.argv[1]
    code = sys.stdin.read()

    if not code.strip():
        print(json.dumps({"error": "No code received"}))
        sys.exit(1)

    try:
        ai_result = ai_service.generate_testcases(code, api_key)
    except Exception as e:
        print(json.dumps({"error": f"AI service failed: {str(e)}"}))
        sys.exit(1)

    if "error" in ai_result:
        print(json.dumps({"error": ai_result["error"]}))
        sys.exit(1)

    final_output = {"type": "mixed"}

    # Handle script part
    if "script" in ai_result:
        script_results = []
        for case in ai_result["script"].get("testcases", []):
            script_results.append({
                "input": case.get("input"),
                "expected": case.get("expected"),
                "actual": "N/A (script)",
                "status": "INFO",
                "remarks": "Run manually with given input"
            })
        final_output["script"] = {
            "complexity": ai_result["script"].get("complexity", "N/A"),
            "results": script_results
        }

    # Handle function part
    if "functions" in ai_result:
        all_function_results = []
        for func_data in ai_result["functions"]:
            func_name = func_data.get("function")
            testcases = func_data.get("testcases", [])
            complexity = func_data.get("complexity", "N/A")

            if func_data.get("error"):
                all_function_results.append({
                    "function": func_name,
                    "complexity": complexity,
                    "results": [{"status": "ERROR", "remarks": func_data["error"]}]
                })
                continue

            # Suppress stdout during judge execution
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                judge_results = judge_service.run_judge(code, testcases, func_name=func_name)
            finally:
                sys.stdout = old_stdout

            all_function_results.append({
                "function": func_name,
                "complexity": complexity,
                "results": judge_results
            })
        final_output["functions"] = all_function_results

    # Print final JSON to stdout
    print(json.dumps(final_output))