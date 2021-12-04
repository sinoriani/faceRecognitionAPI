from flask import Flask, redirect, jsonify, request
import os
from werkzeug.utils import secure_filename
from classifier import compare_image, update_listed_files
import cv2
import uuid
import base64
from utils import *
from urllib.parse import unquote



UPLOAD_FOLDER = 'images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_request_file(request):
    if 'file' not in request.files:
        return {'error': 'No file in the request'}
    
    file = request.files['file']

    if file.filename == '':
        return {'error': 'No file in the request'}

    if not allowed_file(file.filename):
        return {'error': 'Wrong file extension'}

    return file


@app.route('/upload_save_picture', methods=['POST'])
def upload_file():
    file = get_request_file(request)
    # print(len(file.read()))
    
    if type(file) is dict and 'error' in file:
        return jsonify(file), 422
    if 'label' not in request.form:
        return jsonify({'error':'Please include a label field in your request'}), 422
    
    # print(len(file.read()))
    filename = request.form['label'] + ' -'+ secure_filename(file.filename)
    filename = uuid.uuid4().hex + '.' + file.filename.split('.')[-1]
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    update_listed_files(file_path, request.form['label'])
    return jsonify({"message":"File saved successfully"}), 200


@app.route('/classify_picture', methods=['POST'])
def classify_picture():
    file = get_request_file(request)

    if 'error' in file:
        return jsonify(file), 422
    else:
        result = compare_image(file)
        return jsonify({"name":result}), 200



@app.route('/my_pictures', methods=['GET'])
def my_pictures():
    label = request.args.get('label')
    label = unquote(label)
    print(label)
    all_images = get_all_images(label)
    return jsonify(all_images)


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5000)
