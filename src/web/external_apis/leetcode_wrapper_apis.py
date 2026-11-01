from flask import Flask, jsonify, request

# Initialize the Flask app correctly
app = Flask(__name__)

@app.route('/problems', methods=['GET'])
def get_problems():
    # Extract the pattern_name from the URL query parameters
    # Example URL: /problems?pattern_name=Sliding%20Window
    pattern_name = request.args.get('pattern_name')
    
    if not pattern_name:
        return jsonify({"error": "Missing pattern_name parameter"}), 400

    # Placeholder logic to fetch actual problems
    # In reality, you'd query a database or LeetCode here based on pattern_name
    mock_problems = [
        f"{pattern_name} Problem 1",
        f"{pattern_name} Problem 2"
    ]
    
    return jsonify({
        "message": "Successfully fetched problems",
        "problems": mock_problems
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)