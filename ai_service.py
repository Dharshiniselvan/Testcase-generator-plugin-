import json
from openai import OpenAI

# ✅ सीधे API key डाल रहे हैं (no environment variable issues)
client = OpenAI(api_key="YOUR_API_KEY_HERE")


def generate_testcases(code):
    prompt = f"""
Analyze the following Python code:

{code}

Generate:
1. At least 5 test cases (include edge cases)
2. Expected outputs
3. Time and space complexity

Return ONLY JSON in this format:
{{
  "testcases": [
    {{"input": "1 2", "output": "3"}},
    {{"input": "5 7", "output": "12"}}
  ],
  "complexity": {{
    "time": "O(n)",
    "space": "O(1)"
  }}
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        ai_output = response.choices[0].message.content.strip()

        # ✅ Clean JSON (handles extra text if AI adds anything)
        start = ai_output.find("{")
        end = ai_output.rfind("}")
        ai_output = ai_output[start:end+1]

        return json.loads(ai_output)

    except Exception as e:
        print("Error:", e)
        return None


# ✅ RUN DIRECTLY
if __name__ == "__main__":
    print("Paste your Python code (press ENTER twice to finish):")

    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)

    code = "\n".join(lines)

    result = generate_testcases(code)

    print("\n=== AI OUTPUT ===\n")

    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Something went wrong.")