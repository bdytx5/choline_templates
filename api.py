from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

def generate_response(prompt):
    curl_command = f"""curl -s http://localhost:11434/api/generate -d '{{"model": "mistral", "prompt":"{prompt}"}}'"""
    
    process = subprocess.Popen(curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    full_response = ""

    while True:
        output_line = process.stdout.readline()
        if not output_line and process.poll() is not None:
            break
        if output_line:
            try:
                response_data = json.loads(output_line.strip())
                full_response += response_data.get("response", "")
            except json.JSONDecodeError:
                return "Invalid response format", 500

    return full_response

@app.route('/predict', methods=['POST'])
def predict():
    # Get data from request
    data = request.json
    user_prompt = data.get('prompt', '')

    # Generate response based on the input prompt
    response = generate_response(user_prompt)

    # Return the generated response
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

