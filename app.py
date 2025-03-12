import os
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv
from backend import get_current_entry

# Load credentials from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/current-entry')
def current_entry():
    entries = get_current_entry()
    return jsonify({"entries": entries})

if __name__ == '__main__':
    app.run(debug=True)
