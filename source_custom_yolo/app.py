import os

from flask import Flask, render_template, request, url_for, redirect, flash, Response
import requests
import cv2

from yolov3.detect import infer_image, load_model, infer_realtime_webcam, infer_video

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config.update(
    ENV='development',
    SECRET_KEY= 'secret-key',
    UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static')
)

 # LOAD YOLO MODEL ONCE
yolo, classes, colors, output_layers = load_model()

# @app.route('/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         if request.form['username'] != 'admin' or request.form['password'] != 'admin':
#             flash('Wrong username or password')
#         else:
#             flash('Sucessfully login in')
#             return redirect(url_for('home'))
#     return render_template('login.html')


@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/detect_mask')
def detect_mask():
    return render_template('detect_mask.html')

@app.route('/detect_mask_result', methods=["POST"])
def detect_mask_result():
    # request the user to upload a file
    image = request.files["file"]
    
        # Create directory to store uploaded image
    upload_dir = "/".join([app.config['UPLOAD_FOLDER'], 'uploads'])
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)

    # Save uploaded image to local storage
    filename = image.filename
    upload_dir = "/".join([upload_dir, filename])
    image.save(upload_dir)

    output_filename, file_extension = os.path.splitext(filename)
    output_filename = output_filename + '_detected' + file_extension

    output_dir = "/".join([app.config['UPLOAD_FOLDER'], 'detected'])
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # Save processed image to local storage
    output_dir = "/".join([output_dir, output_filename])

    # Object detection API
    infer_image(upload_dir, output_dir, yolo, classes, colors, output_layers)

    return render_template('detect_mask_result.html', upload_img=filename, output_img=output_filename)

@app.route('/detect_mask_live')
def detect_mask_live():
    return render_template('detect_mask_live.html')

@app.route('/video_feed')
def video_feed():
    return Response(infer_realtime_webcam(yolo, classes, colors, output_layers),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/video")
def detect_video():
    return render_template("detect_video.html")

@app.route("/video_result", methods=["POST"])
def detect_video_result():
    # request the user to upload a file
    vid = request.files["file"]
    
        # Create directory to store uploaded image
    upload_dir = "/".join([app.config['UPLOAD_FOLDER'], 'videos'])
    if not os.path.isdir(upload_dir):
        os.mkdir(upload_dir)

    # Save uploaded image to local storage
    filename = vid.filename
    upload_dir = "/".join([upload_dir, filename])
    vid.save(upload_dir)

    output_filename, file_extension = os.path.splitext(filename)
    mp4_filename = output_filename + '_detected'
    avi_filename = output_filename + '_detected' + ".avi"
    

    output_dir = "/".join([app.config['UPLOAD_FOLDER'], 'videos'])
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # Save processed image to local storage
    avi_output_dir = "/".join([output_dir, avi_filename])
    mp4_output_dir = "/".join([output_dir, mp4_filename])

    # Object detection API
    infer_video(upload_dir, avi_output_dir, yolo, classes, colors, output_layers)

    convert_avi_to_mp4(avi_output_dir, mp4_output_dir)

    return render_template("detect_video_result.html", upload_vid=filename, output_vid= mp4_filename + file_extension)


def convert_avi_to_mp4(avi_file_path, output_name):
    os.popen("ffmpeg -i '{input}' -ac 2 -b:v 2000k -c:a aac -c:v libx264 -b:a 160k -vprofile high -bf 0 -strict experimental -f mp4 '{output}.mp4'".format(input = avi_file_path, output = output_name))
    return True


if __name__ == "__main__":
    app.run(debug=True)