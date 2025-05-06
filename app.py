from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
from backend import get_current_entry


# Load credentials from .env file
load_dotenv()

app = Flask(__name__, 
    static_url_path='',
    static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/now/api/current-entry')
def current_entry():
    try:
        entries = get_current_entry()
        return jsonify({"entries": entries})
    except Exception as e: 
        return jsonify({"error": str(e)}), 500  # Return a proper error response
