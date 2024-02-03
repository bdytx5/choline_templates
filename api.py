from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    # Get data from request
    data = request.json
    user_input = data.get('input', '')

    # Simply return the input received
    return jsonify({"input_received": user_input})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

