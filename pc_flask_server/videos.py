from flask import (
    Flask, flash, Blueprint, g, redirect, render_template, request, url_for, make_response, send_file, send_from_directory, current_app
)

from pc_flask_server.email_utils import send_mail


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
    video_names = []

    for file in os.listdir(app.root_path+'/media'):
        lc_filename = file.lower()
        if lc_filename.endswith(".jpg") or lc_filename.endswith(".gif") or lc_filename.endswith(".png"):
            media_names.append(file)
        if lc_filename.endswith(".webm") or lc_filename.endswith(".mp4") or lc_filename.endswith(".mov"):
            video_names.append(file)
    selected_media = ''
    if request.method == 'POST':
        content = request.get_json(force=True)
        selected_media = content['file_name']
        print (selected_media)
        return render_template('front/selected_media.html', selected_media=selected_media)

    return render_template('front/slideshow.html',media_names=media_names)

@bp.route('/view', methods=('GET', 'POST'))
def slideshow_view():
    selected_media = request.args.get('selected')
    media_type = ''
    lc_filename = selected_media .lower()
    if lc_filename.endswith(".jpg") or lc_filename.endswith(".gif") or lc_filename.endswith(".png"):
        media_type = 'image'
    if lc_filename.endswith(".webm") or lc_filename.endswith(".mp4") or lc_filename.endswith(".mov"):
        media_type = 'video'
    return render_template('front/selected_media.html', selected_media=selected_media, media_type=media_type)

@bp.route('/video', methods=('GET', 'POST'))
def video():

    return render_template('front/camera.html')

@bp.route('/video/upload', methods=('POST',))
def video_upload():
    if request.method == 'POST':
        file = request.files['file']
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H-%M-%S')
        filename = st+'.webm'
        filepath = app.root_path+'/media/recorded/'+filename
        file.save(filepath)
        send_mail( ["csci5127.grandtotem@gmail.com"], "Your grandparent has sent you a new message!", "Consider reply to the message.", [filepath] )
    return 'video saved'


@bp.route('/media_files/<filename>')
def media_files(filename):
    google_drive_dir = current_app.config['GOOGLE_DRIVE_DIR']
    return send_from_directory(google_drive_dir, filename)
