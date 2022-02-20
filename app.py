import os
from flask import Flask, request, redirect, render_template, jsonify
import easyocr
import PIL
from PIL import Image, ImageOps
import base64
import numpy as np
import io

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024*5

# Web server
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)

        lang = str(request.form['lang'])
        file = np.array(PIL.Image.open(request.files['file']).convert("RGB"))
        reader = easyocr.Reader(['ko'], gpu=True, recog_network="korean", user_network_directory="user_network", model_storage_directory="model", download_enabled=False)
        response = reader.readtext(file)

        return jsonify(response)
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def checkHealth():
	return "Pong",200

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('index.html', result = 'The image size is too large'), 413

if __name__ == '__main__':
    app.run(debug=True, port=8000, host='0.0.0.0', threaded=True)
