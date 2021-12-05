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
    # file = get_request_file(request)
    
    # if type(file) is dict and 'error' in file:
    #     return jsonify(file), 422
    if 'base64' not in request.json:
        return jsonify({'error':"please incldue a base64 field"}), 422
    if 'label' not in request.json:
        return jsonify({'error':'Please include a label field in your request'}), 422
    
    # save b64 to file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uuid.uuid4().hex +".jpeg")

    from PIL import Image
    import io
    image = base64.b64decode(request.json.get('base64').encode())       
    # fileName = 'test.jpeg'

    img = Image.open(io.BytesIO(image))
    img.save(file_path, 'jpeg')


    # with open( file_path, "wb") as fh:
    #     fh.write(base64.decodebytes(request.json.get('base64').encode()))
    # filename = request.form['label'] + ' -'+ secure_filename(file.filename)
    # filename = uuid.uuid4().hex + '.' + file.filename.split('.')[-1]
    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    update_listed_files(file_path, request.json['label'])
    print('saved image', request.json['label'])
    return jsonify({"message":"File saved successfully"}), 200


@app.route('/classify_picture', methods=['POST'])
def classify_picture():
    # file = get_request_file(request)
    base64_image = request.json.get('base64').encode()

    if 'base64' not in request.json:
        return jsonify({'error':"please incldue a base64 field"}), 422
    else:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uuid.uuid4().hex +".png")
        with open( file_path, "wb") as fh:
            fh.write(base64.decodebytes(request.json.get('base64').encode()))
         
        result = compare_image(file_path)
        print('name classified: ', result)

        os.remove(file_path)

        return jsonify({"name":result}), 200



@app.route('/my_pictures', methods=['GET'])
def my_pictures():
    label = request.args.get('label')
    label = unquote(label)
    all_images = get_all_images(label)
    print("GET images:", label)
    return jsonify({"result":all_images}); 200


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5001)
