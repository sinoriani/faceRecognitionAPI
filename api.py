from flask import Flask, redirect, jsonify, request
import os
from werkzeug.utils import secure_filename
from classifier import compare_image, update_listed_files
import face_recognition 
import cv2
import uuid
import base64
from utils import *
from urllib.parse import unquote
import cv2

UPLOAD_FOLDER = 'images/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload_save_picture', methods=['POST'])
def upload_file():
    if 'base64' not in request.json:
        return jsonify({'error':"please incldue a base64 field"}), 422
    if 'label' not in request.json:
        return jsonify({'error':'Please include a label field in your request'}), 422
    
    # save b64 to file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uuid.uuid4().hex +".jpeg")

    from PIL import Image
    import io
    image = base64.b64decode(request.json.get('base64').encode())       

    img = Image.open(io.BytesIO(image))
    img.save(file_path, 'jpeg')


    update_listed_files(file_path, request.json['label'])
    print('saved image', request.json['label'])
    return jsonify({"message":"File saved successfully"}), 200


@app.route('/classify_picture', methods=['POST'])
def classify_picture():
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


@app.route('/blur_picture', methods=['POST'])
def blur_picture():
    base64_image = request.json.get('base64').encode()

    if 'base64' not in request.json:
        return jsonify({'error':"please incldue a base64 field"}), 422
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uuid.uuid4().hex +".png")
    with open( file_path, "wb") as fh:
        fh.write(base64.decodebytes(request.json.get('base64').encode()))
    image = face_recognition.load_image_file(file_path)
    face_locations = face_recognition.face_locations(image)
    for (y1, x2, y2 ,x1) in face_locations:
        # image = cv2.rectangle(image, (x1, y1), (x2, y2), (255,0,0), 3)
        w, h = x2 - x1, y2 - y1

        # Grab ROI with Numpy slicing and blur
        ROI = image[y1:y1+h, x1:x1+w]
        blur = cv2.GaussianBlur(ROI, (51,51), 0) 

        # Insert ROI back into image
        image[y1:y1+h, x1:x1+w] = blur
    
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    retval, buffer = cv2.imencode('.png', image)
    cv2.imwrite(file_path, image)

    return jsonify({"result":base64.b64encode(buffer).decode('utf-8')}), 200



@app.route('/black_white_picture', methods=['POST'])
def black_white_picture():
    base64_image = request.json.get('base64').encode()

    if 'base64' not in request.json:
        return jsonify({'error':"please incldue a base64 field"}), 422
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uuid.uuid4().hex +".png")
    with open( file_path, "wb") as fh:
        fh.write(base64.decodebytes(request.json.get('base64').encode()))
    
    image = cv2.imread(file_path)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    retval, buffer = cv2.imencode('.png', image)
    cv2.imwrite(file_path, image)

    return jsonify({"result":base64.b64encode(buffer).decode('utf-8')}), 200



@app.route('/negative_picture', methods=['POST'])
def negative_picture():
    base64_image = request.json.get('base64').encode()

    if 'base64' not in request.json:
        return jsonify({'error':"please incldue a base64 field"}), 422
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], uuid.uuid4().hex +".png")
    with open( file_path, "wb") as fh:
        fh.write(base64.decodebytes(request.json.get('base64').encode()))
    
    image = cv2.imread(file_path)

    image = cv2.bitwise_not(image)

    retval, buffer = cv2.imencode('.png', image)
    cv2.imwrite(file_path, image)

    return jsonify({"result":base64.b64encode(buffer).decode('utf-8')}), 200



@app.route('/my_pictures', methods=['GET'])
def my_pictures():
    label = request.args.get('label')
    label = unquote(label)
    all_images = get_all_images(label)
    print("GET images:", label)
    return jsonify({"result":all_images}); 200


if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5000)
