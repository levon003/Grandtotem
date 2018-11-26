from flask import Flask, render_template, redirect, url_for, request
import RPi.GPIO as io
import threading
import requests
import os

pcFlaskServerEndpoint = "http://er-10-131-200-87.wireless.umn.edu:5001/"

io.setmode(io.BCM)
door_pin = 23
led_pin = 17
touch_pin = 18
io.setup(door_pin, io.IN, pull_up_down=io.PUD_UP)
io.setup(led_pin, io.OUT)
io.setup(touch_pin, io.IN, pull_up_down=io.PUD_DOWN)

shouldGalleryBeUpdated = False

dir = './static/gdrive'

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('gallery'))

@app.route('/gallery')
def gallery():
    imgList = loadImg()
    videoList = loadVideo()
    return render_template('home.html', imgList=imgList, videoList=videoList)

@app.route('/gallery/update', methods=['POST'])
def galleryUpdate():
    if request.method == 'POST':
        imgList = loadImg()
        videoList = loadVideo()
        return render_template('homesfd.html', imgList=imgaList, videoList=videoList)
    
@app.route('/shouldGalleryBeUpdated', methods=['POST'])
def checkForGalleryUpdate():
    global shouldGalleryBeUpdated
    if (!shouldGalleryBeUpdated):
        return make_response("No", 200)
    else:
        shouldGalleryBeUpdated = False
        return make_response("Yes", 200)
    

@app.route('/gallery/<string:fileName>')
def selection(fileName):
    json = {'fileName':fileName}
    res = requests.post(pcFlaskServerEndpoint + 'gallery/selection', json=json)

def loadImg():
    imgList = []
    for filename in os.listdir(dir):
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            imgList.append(filename)
        else:
            continue
    
    return imgList

def loadVideo():
    videoList = []
    for filename in os.listdir(dir):
        if filename.endswith(".webm") or filename.endswith(".mp4"):
            videoList.append(filename)
        else:
            continue
        
    return videoList
            
def check_pin(prev_state):
    switch_state = io.input(door_pin)
    led_on = switch_state
    touch_active = io.input(touch_pin)
    
    if switch_state:
        test_json = {'request_type': 'activate'}
        print("open")
    else:
        test_json = {'request_type': 'deactivate'}
        print("close")
        
    if led_on:
        io.output(led_pin, io.HIGH) #check if led signal is set to active then turns on LEDs
    else:
        io.output(led_pin, io.LOW) # leave the pin off if there is no signal
        
    if touch_active:
        print("touch has been sensed") # capacitive bar has registered a touch
        res = requests.post(pcFlaskServerEndpoint + 'touch/grandparent')
    
    threading.Timer(1.0, check_pin, [switch_state]).start()
    
    if (switch_state != prev_state):
        res = requests.post(pcFlaskServerEndpoint + '5001/control/camera', json = test_json)

def check_media_folder(prev_folder_contents):
  global shouldGalleryBeUpdated
  # uses timed threads to recursively check for new items in the folder every 10 seconds
  folder_contents = []
  new_file = False
  for root, dirs, files in os.walk("./static/gdrive"):
    for filename in files:
      folder_contents.append(filename)
      if not filename in prev_folder_contents:
        print(filename)
        shouldGalleryBeUpdated = True
  threading.Timer(10.0, check_media_folder, [folder_contents]).start()


def get_folder_contents():
    # simply returns list of contents of folder
    folder_contents = []
    for root, dirs, files in os.walk("./static/gdrive"):
        for filename in files:
            folder_contents.append(filename)
    return folder_contents

if __name__ == '__main__':
    check_pin(io.input(door_pin))
    check_media_folder(get_folder_contents())
    app.run()
