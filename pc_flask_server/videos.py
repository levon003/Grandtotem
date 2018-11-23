from flask import (
    Flask, flash, Blueprint, g, redirect, render_template, request, url_for, make_response, send_file, send_from_directory, current_app
)

import requests
import smtplib
import os
import datetime
import time

bp = Blueprint('videos', __name__)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'media')

@bp.route('/slideshow', methods=('GET', 'POST'))
def slideshow():
    ## media_directory = os.path.join(app.instance_path, 'media')
    media_names = []
    for file in os.listdir('/Users/yyyuan/Documents/GitHub/Grandtotem/pc_flask_server/media'):
        if file.endswith(".jpg") or file.endswith(".png"):
            media_names.append(file)
        if file.endswith(".webm") or file.endswith(".mp4"):
            video_names.append(file)
    print(media_names)

    return render_template('front/slideshow.html',media_names=media_names)


@bp.route('/video', methods=('GET', 'POST'))
def video():

    return render_template('front/camera.html')

@bp.route('/video/upload', methods=('POST',))
def video_upload():
    if request.method == 'POST':
        file = request.files['file']
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        filename = st+'.webm'
        print (filename)
        file.save(app.root_path+'/media/'+filename)
    return 'video saved'


@bp.route('/media_files/<filename>')
def media_files(filename):
    google_drive_dir = current_app.config['GOOGLE_DRIVE_DIR']
    return send_from_directory(google_drive_dir, filename)
