from flask import (
    Flask, flash, Blueprint, g, redirect, render_template, request, url_for, make_response, send_file, send_from_directory, current_app
)

import requests
import smtplib
import os
import datetime
import time

from email.mime.multipart  import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders

bp = Blueprint('videos', __name__)
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'media')

@bp.route('/slideshow', methods=('GET', 'POST'))
def slideshow():
    ## media_directory = os.path.join(app.instance_path, 'media')
    media_names = []
    video_names = []

    for file in os.listdir(app.root_path+'/media'):
        if file.endswith(".jpg") or file.endswith(".png"):
            media_names.append(file)
        if file.endswith(".webm") or file.endswith(".mp4"):
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
    if selected_media.endswith(".jpg") or selected_media.endswith(".png"):
        media_type = 'image'
    if selected_media.endswith(".webm") or selected_media.endswith(".mp4"):
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
        filepath = app.root_path+'/media/'+filename
        file.save(filepath)
        send_mail( ["csci5127.grandtotem@gmail.com"], "New Message from GGrandparent", "New Message", [filepath] )
    return 'video saved'


@bp.route('/media_files/<filename>')
def media_files(filename):
    google_drive_dir = current_app.config['GOOGLE_DRIVE_DIR']
    return send_from_directory(google_drive_dir, filename)



USERNAME = "csci5127.grandtotem@gmail.com"
PASSWORD = "abcd_1234"

def send_mail(to, subject, text, files=[]):
    assert type(to)==list
    assert type(files)==list

    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'% os.path.basename(file))
        msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.ehlo_or_helo_if_needed()
    server.login(USERNAME,PASSWORD)
    server.sendmail(USERNAME, to, msg.as_string())
    server.quit()
    print ('send email')
