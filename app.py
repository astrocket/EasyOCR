import os
import io
import PIL
import base64
import logging
import traceback
import easyocr
import numpy as np
from PIL import Image, ImageOps
from time import strftime
from flask import Flask, request, redirect, render_template, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from waitress import serve
from logging.handlers import RotatingFileHandler

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024*5
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["5/second"]
)

# Web server
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
@limiter.limit("1/second", override_defaults=False)
def upload_file():
    if 'file' not in request.files:
        print('no file')
        return redirect(request.url)

    lang = str(request.form['lang'])
    print(lang)
    file = np.array(PIL.Image.open(request.files['file']).convert("RGB"))
    reader = easyocr.Reader(['ko'], gpu=True, recog_network="korean", user_network_directory="user_network", model_storage_directory="model", download_enabled=False)
    result = reader.readtext(file)
    logger.debug(result)

    res_list = list()

    for i in result:
        res_list.append(i[1])

    res_str = ''

    for i in res_list:
        res_str = res_str + ' ' + i

    return jsonify({ "result": res_str }), 200

@app.route('/health', methods=['GET'])
def checkHealth():
	return jsonify({ "env": os.environ['FLASK_ENV'] }), 200

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.debug('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response

@app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, tb)
    return 500

# https://gist.github.com/alexaleluia12/e40f1dfa4ce598c2e958611f67d28966
if __name__ == '__main__':
    handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    serve(app, host="0.0.0.0", port=8000)