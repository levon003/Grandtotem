from flask import Flask, render_template, redirect, url_for, request, make_response
import RPi.GPIO as io
import threading
import requests
import os

# The endpoint to which POSTs are made...
# In general, this will require port-forwarding from the Raspberry Pi to the PC
pcFlaskServerEndpoint = "http://localhost:5001/"

io.setmode(io.BCM)
door_pin = 23
led_pin = 17
touch_pin = 18
io.setup(door_pin, io.IN, pull_up_down=io.PUD_UP)
io.setup(led_pin, io.OUT)
io.output(led_pin, io.LOW)
print("Initialized LED pin to off.")
io.setup(touch_pin, io.IN, pull_up_down=io.PUD_DOWN)

shouldGalleryBeUpdated = False

# this list stores images that
unselected_images = []
unselected_images_lock = threading.Lock()

dir = './static/gdrive'

app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('gallery'))


@app.route('/gallery')
def gallery():
    imgList = loadImg()
    videoList = loadVideo()
    print("Retrieved %d images and %d videos for rendering in the gallery." % (len(imgList), len(videoList)))

    media_list = []
    with unselected_images_lock:
        for filename in imgList:
            upload_time = os.path.getmtime(os.path.join(dir, filename))
            new_status = "not new"
            if filename in unselected_images:
                new_status = "new"
            media_item = {
                "filename": filename,
                "media_type": "image",
                "new_status": new_status,
                "upload_time": upload_time
            }
            media_list.append(media_item)
        for filename in videoList:
            upload_time = os.path.getmtime(os.path.join(dir, filename))
            new_status = "not new"
            if filename in unselected_images:
                new_status = "new"
            media_item = {
                "filename": filename,
                "media_type": "video",
                "new_status": new_status,
                "upload_time": upload_time
            }
            media_list.append(media_item)
    media_list.sort(key=lambda d: d['upload_time'], reverse=True)

    return render_template('home.html', mediaList=media_list)


# This endpoint is no longer used (deprecated)
@app.route('/gallery/update', methods=['POST'])
def galleryUpdate():
    if request.method == 'POST':
        return make_response("OK", 200)
        #imgList = loadImg()
        #videoList = loadVideo()
        #return render_template('home.html', imgList=imgList, videoList=videoList)


@app.route('/shouldGalleryBeUpdated', methods=['POST'])
def checkForGalleryUpdate():
    global shouldGalleryBeUpdated
    if not shouldGalleryBeUpdated:
        return make_response("No", 200)
    else:
        shouldGalleryBeUpdated = False
        print("Informing Raspberry Pi frontend that the gallery-view should be refreshed.")
        return make_response("Yes", 200)


@app.route('/gallery/<string:fileName>', methods=("GET", "POST",))
def selection(fileName):
    json = {'fileName': fileName}
    res = requests.post(pcFlaskServerEndpoint + 'gallery/selection', json=json)
    if res.status_code == 200:
        print("Gallery selection made successfully... checking for unselected image.")
        with unselected_images_lock:
            if fileName in unselected_images:
                print("A previously unselected media ('%s') has been selected." % fileName)
                unselected_images.remove(fileName)
                update_led()
        return make_response("OK", 200)
    else:
        return make_response("POST failed.", 500)


def loadImg():
    imgList = []
    for filename in os.listdir(dir):
        lc_filename = filename.lower()
        if lc_filename.endswith(".jpg") \
                or lc_filename.endswith(".jpeg") \
                or lc_filename.endswith(".png") \
                or lc_filename.endswith(".gif"):
            imgList.append(filename)
        else:
            continue

    return imgList


def loadVideo():
    videoList = []
    for filename in os.listdir(dir):
        lc_filename = filename.lower()
        if lc_filename.endswith(".webm") or lc_filename.endswith(".mp4") or lc_filename.endswith(".mov"):
            videoList.append(filename)
        else:
            continue

    return videoList


def update_led():  # this function assumes the unselected_images_lock is currently held
    print("Updating LED...")
    if len(unselected_images) > 0:
        io.output(led_pin, io.HIGH)
        print("Setting LED output to HIGH, as there are %d unselected media." % len(unselected_images))
    else:  # there are no unselected images
        io.output(led_pin, io.LOW)
        print("Setting LED output to LOW, as there are no unselected media.")


def check_pin(prev_state):
    switch_state = io.input(door_pin)
    touch_active = io.input(touch_pin)

    if switch_state:
        test_json = {'request_type': 'activate'}
        print("open")
    else:
        test_json = {'request_type': 'deactivate'}
        print("close")
    if switch_state != prev_state:
        print("POSTing camera request.")
        res = requests.post(pcFlaskServerEndpoint + 'control/camera', json=test_json)
        print(res.status_code, res)

    if touch_active:
        print("touch has been sensed")  # capacitive bar has registered a touch
        res = requests.post(pcFlaskServerEndpoint + 'touch/grandparent')
        if res.status_code == 200:
            print("Touch sent successfully to server.")
        else:
            print("Error sending touch to server.")
            print(res)

    threading.Timer(1.0, check_pin, [switch_state]).start()


def check_media_folder(prev_folder_contents):
    global shouldGalleryBeUpdated
    # uses timed threads to recursively check for new items in the folder every 10 seconds
    folder_contents = []
    for root, dirs, files in os.walk("./static/gdrive"):
        if root.endswith("recorded"):
            continue
        for filename in files:
            folder_contents.append(filename)
            if not filename in prev_folder_contents:
                print("Found new file '%s' in gdrive folder." % filename)
                with unselected_images_lock:
                    unselected_images.append(filename)
                    update_led()
                shouldGalleryBeUpdated = True
    threading.Timer(10.0, check_media_folder, [folder_contents]).start()


def get_folder_contents():
    # simply returns list of contents of folder
    folder_contents = []
    for root, dirs, files in os.walk("./static/gdrive"):
        if root.endswith("recorded"):
            continue
        for filename in files:
            folder_contents.append(filename)
    return folder_contents


if __name__ == '__main__':
    check_pin(io.input(door_pin))
    check_media_folder(get_folder_contents())
    app.run()
