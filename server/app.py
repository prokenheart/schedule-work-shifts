from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import os
from dotenv import load_dotenv

load_dotenv()  # Load biến từ .env nếu có

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)  # Cho phép frontend từ domain khác gọi API (Netlify/Vercel)

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

# Serve static files (CSS, JS)
@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)

@app.route('/api/schedule', methods=['GET'])  # GET cho đơn giản
def schedule():
    try:
        py_path = os.path.join(os.path.dirname(__file__), 'scheduler.py')
        result = subprocess.run(['python', py_path], capture_output=True, text=True, env=os.environ)
        if result.returncode != 0:
            return jsonify({"status": "error", "message": result.stderr}), 500
        data = json.loads(result.stdout)
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run()