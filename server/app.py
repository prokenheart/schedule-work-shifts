from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from scheduler import run_scheduler   #  IMPORT TRỰC TIẾP

app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)

@app.route('/api/schedule', methods=['GET'])
def schedule():
    try:
        data = run_scheduler()   # GỌI HÀM, KHÔNG CHẠY PYTHON
        return jsonify(data)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run()
