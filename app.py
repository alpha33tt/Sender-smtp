import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for API keys and usage limits
api_keys = {}

# Generate API Key Endpoint
@app.route('/generate_api_key', methods=['GET'])
def generate_api_key():
    api_key = str(uuid.uuid4())  # Generate a unique API key
    api_keys[api_key] = {'emails_sent': 0}  # Store the API key and track the emails sent
    return jsonify({'api_key': api_key, 'message': 'API key generated successfully'})

# Send Email Endpoint (This is where the emails will be "sent")
@app.route('/send_email', methods=['POST'])
def send_email():
    api_key = request.headers.get('API-Key')

    # Check if API key is valid
    if not api_key or api_key not in api_keys:
        return jsonify({'error': 'Please generate an API key first!'}), 403

    # Extract email details from the request
    data = request.json
    from_email = data.get('from_email')
    to_emails = data.get('to_emails', [])
    subject = data.get('subject', 'No Subject')
    body = data.get('body', 'No Content')

    # Validate required fields
    if not from_email or not to_emails or not subject or not body:
        return jsonify({'error': 'Missing required fields'}), 400

    # "Send" the email (for demo purposes, we just track the sent emails)
    api_keys[api_key]['emails_sent'] += 1

    return jsonify({'message': f'{len(to_emails)} emails sent successfully!'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
