import json
import google.generativeai as genai

# ✅ Using Gemini (Free & Reliable for 15 days)
genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_testcases(code):
    prompt = f"""
    Analyze this Python code:
    {code}

    Generate 5 test cases. 
    Return ONLY a JSON object with this EXACT structure:
    {{
      "testcases": [
        {{"input": [1, 2], "expected": 3}},
        {{"input": [-1, 1], "expected": 0}}
      ],
      "complexity": "O(n)"
    }}
    Important: 'input' must be a LIST of arguments.
    """

    try:
        response = model.generate_content(prompt)
        # Find the JSON part in the AI text
        text = response.text
        start = text.find("{")
        end = text.rfind("}")
        return json.loads(text[start:end+1])
    except Exception as e:
        print(f"AI Error: {e}")
        return None

if __name__ == "__main__":
    # Test it locally
    sample = "def add(a, b): return a + b"
    print(generate_testcases(sample))
