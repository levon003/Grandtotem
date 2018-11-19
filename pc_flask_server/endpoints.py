from flask import (
    Blueprint, g, redirect, render_template, request, url_for, make_response, send_file, send_from_directory, current_app
)

import requests
import smtplib
import os

bp = Blueprint('endpoints', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        # TODO Should return the response of the post...
        redirect_url = url_for('index',
                               query=request.form.get('query', '')
                               )
        return redirect(redirect_url)

    query_str = request.args.get('query', '')
    if query_str.strip() != "":
        print(query_str)

    return render_template('index.html')

@bp.route('/control/camera', methods=('GET', 'POST'))
def view_camera_controls():
    if request.method == 'POST':
        request_type = request.form['request_type']
        if request_type == "activate":
            if not handle_activate_camera():
                return make_response("Failed to activate camera.", 400)
        elif request_type == "deactivate":
            if not handle_deactivate_camera():
                return make_response("Failed to deactivate camera.", 400)
        else:
            return make_response("Unknown camera control request.", 400)
        return make_response("OK", 200)
    # Else, this is a GET, so render the template
    return render_template('camera_control.html')


@bp.route('/media/<media_filename>', methods=('GET',))
def get_media(media_filename):
    google_drive_dir = current_app.config['GOOGLE_DRIVE_DIR']
    media_filepath = os.path.join(google_drive_dir, media_filename)
    if not os.path.exists(media_filepath):
        return make_response(f"Media filename '{media_filename}' not found in Google Drive folder.", 400)

    return send_from_directory(google_drive_dir, media_filepath)


@bp.route('/gallery/selection', methods=('POST',))
def make_gallery_selection():
    if request.method != 'POST':
        return make_response("Can only POST to this endpoint.", 400)

    request_json = request.get_json(force=True)
    if 'filename' not in request_json:
        return make_response("Expected to be provided with a filename key in this request.", 400)
    selected_filename = request_json['filename']

    if display_media(selected_filename):
        return make_response("OK", 200)
    else:
        return make_response("Could not display the requested gallery selection.", 400)


@bp.route('/touch/grandparent', methods=('POST',))
def make_grandparent_touch():
    if request.method != 'POST':
        return make_response("Can only POST to this endpoint.", 400)

    send_touch_notification_to_grandchild()
    return make_response("OK", 200)


@bp.route('/video/recorded', methods=('POST',))
def receive_recorded_video():
    if request.method != 'POST':
        return make_response("Can only POST to this endpoint.", 400)

    # TODO need to receive the video here, either the raw bytes or the filename of the created file
    return make_response("OK", 200)


def display_media(filename):
    # Attempt to display the given filename
    # If the filename can't be found or it can't be displayed, return False
    # TODO Figure out how Irene wants to do this...
    
    return True


def send_touch_notification_to_grandchild():
    # TODO Include a system for injecting the proper authentication details from an external config file
    send_email("test_user", "password", "test_user@gmail.com",
               "Your grandparent has touched the grandtotem!",
               "Consider sending them a quick message.")
    return True


def send_gallery_update_request():
    """
    Requests that the server running the gallery display will update appropriately.
    :return: True if the request succeeded, false otherwise.
    """
    res = requests.post('http://127.0.0.1:5000/gallery/update')
    return res.status_code != 200


def send_led_update_request(led_color):
    """
    Requests that the server update the LEDs
    :return: True if the request succeeded, false otherwise.
    """
    led_json = {'color': led_color}
    res = requests.post('http://127.0.0.1:5000/led/update', json=led_json)
    return res.status_code != 200


def handle_new_grandchild_media():
    # TODO Call this function when the grandchild sends new media to the grandparent
    send_led_update_request("white")
    send_gallery_update_request()
    return True


def handle_new_grandchild_touch():
    # TODO Call this function when the client sends a "touch" to their grandparent
    send_led_update_request("white")
    return True


def handle_activate_camera():
    return True


def handle_deactivate_camera():
    return True


def send_email(user, pwd, recipient, subject, body):
    # https://stackoverflow.com/a/12424439
    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
    except Exception as ex:
        print(ex)
        return False
    return True
