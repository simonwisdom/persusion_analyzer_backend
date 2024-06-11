import logging
from flask import Flask
from flask_cors import CORS
from fetch_profile import fetch_profile_endpoint
from analyze_profile import analyze_profile_endpoint
from chatbot import chatbot_endpoint

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["persuasion-analyzer-frontend-4x7xb1adg-simonwisdoms-projects.vercel.app"]}})

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


@app.route('/fetch-profile', methods=['POST'])
def fetch_profile():
    return fetch_profile_endpoint()

@app.route('/analyze-profile', methods=['POST'])
def analyze_profile():
    return analyze_profile_endpoint()

@app.route('/messages', methods=['POST'])
def messages_endpoint():
    return chatbot_endpoint()

if __name__ == '__main__':
    app.run(debug=True)