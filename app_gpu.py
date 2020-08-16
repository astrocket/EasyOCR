import os
from flask import Flask, request, send_file, flash, redirect, render_template, url_for, jsonify
import easyocr
from werkzeug.utils import secure_filename
import PIL
from PIL import Image, ImageOps
import base64
import cv2
import numpy as np
import tempfile
import io
from queue import Queue, Empty
import time
import threading



UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024*5

############
requests_queue = Queue()
BATCH_SIZE = 1
CHECK_INTERVAL = 0.1

def handle_requests_by_batch():
    while True:
        requests_batch = []
        while not (len(requests_batch) >= BATCH_SIZE):
            try:
                requests_batch.append(requests_queue.get(timeout=CHECK_INTERVAL))
            except Empty:
                continue
            batch_outputs = []
            for request in requests_batch:
                batch_outputs.append(run(request['input'][0], request['input'][1]))

            for request, output in zip(requests_batch, batch_outputs):
                request['output'] = output
                
threading.Thread(target=handle_requests_by_batch).start()

def run(file, lang):
    
    imgFile = np.array(PIL.Image.open(file).convert("RGB"))
        
    reader = easyocr.Reader([lang, 'en'])
    text = reader.readtext(imgFile)
    res_list = list()
    for i in text:
        res_list.append(i[1])
    
    res_str = ''

    for i in res_list:
        res_str = res_str + ' ' + i 

    #image show
    imgFile = PIL.Image.fromarray(imgFile)
    img_io = io.BytesIO()
    imgFile.save(img_io, 'jpeg', quality=100)
    img_io.seek(0)

    img = base64.b64encode(img_io.getvalue())
    

    return [res_str, img]

##############

# Web server
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# @app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        lang = str(request.form['lang'])
        file = request.files['file']

        try:
            PIL.Image.open(file).convert("RGB")
        except Exception: 
            return render_template('index.html', result = 'Import image please'), 400

        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        

        # stateless image
        if requests_queue.qsize() >= BATCH_SIZE:
            return render_template('index.html', result = 'TooMany requests try again'), 429

        req = {
            'input': [file, lang]
        }
        requests_queue.put(req)

        while 'output' not in req:
            time.sleep(CHECK_INTERVAL)
        [res, img] = req['output']
        return render_template('index.html', result=str(res), rawimg=img.decode('ascii'))
            #return redirect(request.url)
    return render_template('index.html')







# Start Swagger API Server
@app.route('/word_extraction', methods=['POST'])
def word_extraction():
    if not request.files.get('base_image'):
        return {'error': 'must have a base image'}, 400

    target_language = str(request.form['language'])
    file = request.files['base_image']

    try:
        PIL.Image.open(file).convert("RGB")
        # base_image = Image.open(request.files['base_image'].stream)
        # base_image.save("img.png")
        # base_image = Image.open("img.png")
    except Exception:
        return {'error': 'please upload image file.'}, 400

    if requests_queue.qsize() >= BATCH_SIZE:
        return {'error': 'TooMany requests try again'}, 429
    
    req = {
        'input': [file, target_language]
    }
    requests_queue.put(req)

    while 'output' not in req:
        time.sleep(CHECK_INTERVAL)
    [res, img] = req['output']
    return str(res)

@app.route('/healthz', methods=['GET'])
def checkHealth():
	return "Pong",200

@app.errorhandler(413)
def request_entity_too_large(error):
    # return {'error': 'File Too Large'}, 413
    return render_template('index.html', result = 'The image size is too large'), 413

if __name__ == '__main__':
    app.run(debug=False, port=8000, host='0.0.0.0', threaded=False)
