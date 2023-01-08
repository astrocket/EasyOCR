import os
import io
import PIL
import json
import base64
import logging
import requests
import traceback
import easyocr
import numpy as np
from PIL import Image
from io import BytesIO
from time import strftime
from urllib.parse import urlparse
from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from waitress import serve
from logging.handlers import RotatingFileHandler

FLASK_ENV = os.environ.get('FLASK_ENV')
API_TOKEN = os.environ.get('API_TOKEN')

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 15
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10/second"]
)
handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
reader = easyocr.Reader(
    ['ko', 'en'],
    gpu=True,
    download_enabled=False,
    recog_network="korean",
    model_storage_directory="model",
    user_network_directory="user_network"
)

def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False

@app.before_request
def verify_authorization():
    if API_TOKEN != None and API_TOKEN != request.headers.get('Authorization'):
        return jsonify({ "message": "authorization failed" }), 401

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
@limiter.limit("5/second", override_defaults=False)
def upload_file():
    image_url = request.json.get('image_url')
    if image_url and uri_validator(image_url):
        file_io = BytesIO(requests.get(image_url).content)
    elif 'file' in request.files:
        file_io = request.files['file']
    else:
        return jsonify({ "message": "analyzable source doesn't exist" }), 400

    file = np.array(Image.open(file_io).convert("RGB"))
    sections = reader.readtext(file)

    result = list()
    for section in sections:
        temp = dict()
        points = list()
        for point in section[0]:
            int_point = list([int(x) for x in point])
            points.append(int_point)
        temp['points'] = points
        temp['name'] = section[1]
        temp['probability'] = float(section[2])
        result.append(temp)

    jsonObj = json.dumps(result, ensure_ascii=False)

    return jsonify(result), 200

@app.route('/health', methods=['GET'])
def checkHealth():
	return jsonify({ "env": FLASK_ENV }), 200

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
           )

@app.after_request
def after_request(response):
    logger.debug(
        '%s %s %s %s %s %s\nparams : %s',
        strftime('[%Y-%b-%d %H:%M]'),
        request.remote_addr,
        request.method,
        request.scheme,
        request.full_path,
        response.status,
        request.data,
    )
    return response

@app.errorhandler(Exception)
def exceptions(e):
    logger.error(
        '%s %s %s %s %s 5xx INTERNAL SERVER ERROR\nparams : %s\n%s',
        strftime('[%Y-%b-%d %H:%M]'),
        request.remote_addr,
        request.method,
        request.scheme,
        request.full_path,
        request.data,
        traceback.format_exc()
    )
    return 500

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=8000)