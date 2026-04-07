from flask import Flask, request, jsonify
from flask_cors import CORS
import ai_service  # Member 1's file
import judge_service  # Member 2's file

app = Flask(__name__)
CORS(app)  # This allows the VS Code Extension to talk to this Python script

@app.route('/test', methods=['POST'])
def handle_test():
    try:
        # 1. Receive the code from VS Code
        data = request.json
        user_code = data.get('code')
        
        if not user_code:
            return jsonify({"error": "No code provided"}), 400

        print(f"--- Processing New Code Request ---")

        # 2. Get Test Cases from AI (Developer 1's logic)
        ai_response = ai_service.generate_testcases(user_code)
        
        if not ai_response or "testcases" not in ai_response:
            return jsonify({"error": "AI failed to generate test cases"}), 500

        # 3. Run the Judge (Developer 2's logic)
        # We pass the user's code and the list of test cases from the AI
        final_results = judge_service.run_judge(user_code, ai_response['testcases'])

        # 4. Send the final Pass/Fail results back to VS Code
        return jsonify(final_results)

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # The server runs on http://localhost:5000
    app.run(port=5000, debug=True)