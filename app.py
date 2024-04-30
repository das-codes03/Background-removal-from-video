from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
import os
import shutil
from flask_cors import CORS
from bgremove import process_video
app = Flask(__name__)
CORS(app)



UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploadVideo', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return 'No video part'

    file = request.files['video']
    if file.filename == '':
        return 'No selected video'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return process_video(filepath, "wp1867864-software-wallpapers.jpg", 1)
    else:
        return 'Invalid file format'

if __name__ == '__main__':
    if os.path.exists('uploads'):
        shutil.rmtree('uploads')
    os.makedirs('uploads')
    app.run(debug=True)
