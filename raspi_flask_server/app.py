from flask import Flask, render_template, redirect, url_for, request
import RPi.GPIO as io
import threading
import requests
import os

io.setmode(io.BCM)
door_pin = 23
io.setup(door_pin, io.IN, pull_up_down=io.PUD_UP)

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
        return render_template('home.html', imgList=imgList, videoList=videoList)

@app.route('/gallery/<string:fileName>')
def selection(fileName):
    json = {'fileName':fileName}
    res = requests.post('http://127.0.0.1:5001/gallery/selection', json=json)

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
    if switch_state:
	test_json = {'request_type': 'activate'}
        print("open")
    else:
	test_json = {'request_type': 'deactivate'}
        print("close")
    
    threading.Timer(10.0, check_pin, [switch_state]).start()
    
    if (switch_state != prev_state):
	res = requests.post("http://er-10-131-200-87.wireless.umn.edu:5001/control/camera", json = test_json)   

if __name__ == '__main__':
    check_pin(io.input(door_pin))
    app.run()
