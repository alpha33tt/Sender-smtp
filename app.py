import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, send_from_directory
import uuid
import os

app = Flask(__name__)

# In-memory storage for API keys and usage limits
api_keys = {}

# Generate API Key Endpoint
@app.route('/generate_api_key', methods=['GET'])
def generate_api_key():
    api_key = str(uuid.uuid4())  # Generate a unique API key
    api_keys[api_key] = {'emails_sent': 0}  # Store the API key and track the emails sent
    return jsonify({'api_key': api_key, 'message': 'API key generated successfully'})

# Serve the index.html file from the static folder
@app.route('/')
def serve_index():
    try:
        return send_from_directory('static', 'index.html')  # Serve your index.html from the 'static' folder
    except FileNotFoundError:
        return jsonify({'error': 'index.html file not found'}), 404

# Send Email Endpoint
@app.route('/send_email', methods=['POST'])
def send_email():
    # Extract the API Key from request headers
    api_key = request.headers.get('API-Key')

    # Check if API key is provided and valid
    if not api_key or api_key not in api_keys:
        return jsonify({'error': 'Please generate an API key first!'}), 403

    # Enforce email limit (10,000 emails per API key)
    if api_keys[api_key]['emails_sent'] >= 10000:
        return jsonify({'error': 'Email limit reached for this API key'}), 403

    # Extract email details from the request
    data = request.json
    from_email = data.get('from_email')
    from_name = data.get('from_name', 'No Name')
    to_emails = data.get('to_emails', [])
    subject = data.get('subject', 'No Subject')

    # Read HTML content from 'index.html' if not provided
    html_content = data.get('html_content', None)
    if not html_content:
        try:
            with open('static/index.html', 'r') as file:
                html_content = file.read()
        except FileNotFoundError:
            return jsonify({'error': 'index.html file not found'}), 400

    # Validate required fields
    if not from_email or not to_emails or not subject or not html_content:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Your SMTP server settings for local testing
        smtp_server = "localhost"  # You can change this to your own SMTP server
        smtp_port = 25  # Use the port appropriate for your SMTP server (25, 587, etc.)

        # Create the SMTP connection
        server = smtplib.SMTP(smtp_server, smtp_port)

        # Send email to each recipient
        for email in to_emails:
            msg = MIMEMultipart()
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_content, 'html'))

            # Send the email
            server.sendmail(from_email, email, msg.as_string())
            api_keys[api_key]['emails_sent'] += 1  # Increment the email count for the API key

        server.quit()  # Close the connection to the SMTP server
        return jsonify({'message': f'{len(to_emails)} emails sent successfully!'})  # Respond with success
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Handle any errors during email sending


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
