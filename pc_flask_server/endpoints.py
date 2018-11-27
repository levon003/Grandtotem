from flask import (
    Blueprint, g, redirect, render_template, request, url_for, make_response, send_file, send_from_directory, current_app
)

import os
import threading

from pc_flask_server.email_utils import send_mail


bp = Blueprint('endpoints', __name__)


file_to_display = None

camera_lock = threading.Lock()
is_camera_active = False
should_camera_be_active = False
should_camera_be_deactivated = False


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
        print(request)
        request_json = request.get_json(force=True)
        print(request_json)
        request_type = request_json['request_type']
        print(request_type)
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

    print(request)
    request_json = request.get_json(force=True)
    if 'fileName' not in request_json:
        return make_response("Expected to be provided with a filename key in this request.", 400)
    selected_filename = request_json['fileName']

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


@bp.route('/shouldFileBeDisplayed', methods=("POST",))
def handle_should_file_be_displayed():
    global file_to_display
    if file_to_display is not None:
        print(f"Resetting filename-to-display, returning filename '{file_to_display}' to frontend request.")
        to_display = file_to_display
        file_to_display = None
        return make_response(to_display, 200)
    return make_response("No", 200)


def display_media(filename):
    global file_to_display
    # TODO Check to make sure the filename actually exists in the local google drive
    print(f"Registering filename '{filename}' as to-be-displayed.")
    file_to_display = filename
    return True


def send_touch_notification_to_grandchild():
    send_mail(["csci5127.grandtotem@gmail.com"],
               "Your grandparent has touched the grandtotem!",
               "Consider sending them a quick message.")
    print("Email sent with touch notification.")
    return True


@bp.route('/shouldCameraViewBeActive', methods=("POST",))
def handle_should_camera_be_active():
    global should_camera_be_active, should_camera_be_deactivated, is_camera_active
    with camera_lock:
        if should_camera_be_active:
            should_camera_be_active = False
            should_camera_be_deactivated = False
            is_camera_active = True
            print("Informing front-end that camera should be active.")
            return make_response("Yes", 200)
    return make_response("No", 200)


@bp.route('/shouldCameraBeDeactivated', methods=("POST",))
def handle_should_camera_be_deactivated():
    global should_camera_be_active, should_camera_be_deactivated, is_camera_active
    with camera_lock:
        if not is_camera_active:
            print("WARNING: Received shouldCameraBeDeactivated request, but internally the camera is not activated.  Consider manually resetting the front-end to the slideshow view.")
        if should_camera_be_deactivated:
            should_camera_be_active = False
            should_camera_be_deactivated = False
            is_camera_active = False
            print("Informing front-end that camera should be deactivated.")
            return make_response("Yes", 200)
    return make_response("No", 200)


def handle_activate_camera():
    global should_camera_be_active, should_camera_be_deactivated
    with camera_lock:
        if is_camera_active:
            print("Received request to activate camera, but the camera is already active. Ignoring request.")
            return True
        else:  # The camera is not yet active
            print(f"Camera registered as should-be-activated. (prev value: {should_camera_be_active})")
            should_camera_be_active = True
            should_camera_be_deactivated = False
    return True


def handle_deactivate_camera():
    global should_camera_be_active, should_camera_be_deactivated
    with camera_lock:
        if not is_camera_active:
            print("Received request to deactivate camera, but the camera is not active. Ignoring request.")
            return True
        print(f"Camera registered as should-be-deactivated. (prev value: {should_camera_be_deactivated})")
        should_camera_be_active = False
        should_camera_be_deactivated = True
    return True