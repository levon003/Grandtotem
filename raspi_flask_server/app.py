from flask import Flask, render_template, redirect, url_for, request
import RPi.GPIO as io
import threading
import requests

io.setmode(io.BCM)
door_pin = 23
io.setup(door_pin, io.IN, pull_up_down=io.PUD_UP)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/photo')
def photo():
    return render_template('photo.html', 
                      photoUrl=request.args.get('photoUrl'))

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
