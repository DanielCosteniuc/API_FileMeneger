from flask import Flask, request, send_from_directory, jsonify, render_template
import os
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 160 * 1024 * 1024  # 160 MB

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def start_page():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if allowed_file(uploaded_file.filename):
        filename = uploaded_file.filename
        destination = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(destination)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'txt', 'docx', 'mp4', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        try:
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'File not found'}), 404


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': f'File {filename} deleted successfully.'}), 200
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/list', methods=['GET'])
def list_files():
    path = request.args.get('path', '')
    full_path = os.path.join(UPLOAD_FOLDER, path)
    
    if not os.path.exists(full_path):
        return jsonify({'error': 'Path not found'}), 404
    
    files = []
    for item in os.listdir(full_path):
        item_path = os.path.join(full_path, item)
        files.append({
            'name': item,
            'is_dir': os.path.isdir(item_path)
        })
    
    return jsonify({'files': files}), 200

@app.route('/server-action', methods=['POST'])
def server_action():
    file_path = request.args.get('filePath')
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], file_path)
    
    
    if os.path.exists(full_path):
        
        subprocess.run(['start', full_path], shell=True)
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Fișierul nu a fost găsit.'}), 404


#deschiderea Microsoft Teams
@app.route('/open-teams', methods=['POST'])
def open_teams():
    try:
        subprocess.run(['start', 'teams'], shell=True)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
