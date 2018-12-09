/*
*  Copyright (c) 2015 The WebRTC project authors. All Rights Reserved.
*
*  Use of this source code is governed by a BSD-style license
*  that can be found in the LICENSE file in the root of the source
*  tree.
*/

// This code is adapted from
// https://rawgit.com/Miguelao/demos/master/mediarecorder.html

'use strict';

/* set up div width and height */
var w = window.innerWidth;
var h = window.innerHeight;

console.log(w);


/* globals MediaRecorder */

const mediaSource = new MediaSource();
mediaSource.addEventListener('sourceopen', handleSourceOpen, false);
let mediaRecorder;
let recordedBlobs;
let sourceBuffer;

const hasEchoCancellation = 0;
const constraints = {
  audio: {
    echoCancellation: {exact: hasEchoCancellation}
  },
  video: {
    width: w, height: h
  }
};
console.log('Using media constraints:', constraints);
init(constraints);

//const errorMsgElement = document.querySelector('span#errorMsg');
const recordedVideo = document.querySelector('video#recorded');
const recordButton = document.querySelector('button#record');
recordButton.addEventListener('click', () => {
  if (recordButton.textContent === 'RECORD') {
    startRecording();
  } else {
    stopRecording();
    recordButton.textContent = 'RECORD';
    //playButton.disabled = false;
    downloadButton.disabled = false;
  }
});

/*
const playButton = document.querySelector('button#play');
playButton.addEventListener('click', () => {
  const superBuffer = new Blob(recordedBlobs, {type: 'video/webm'});
  recordedVideo.src = null;
  recordedVideo.srcObject = null;
  recordedVideo.src = window.URL.createObjectURL(superBuffer);
  recordedVideo.controls = true;
  recordedVideo.play();
});
*/

const downloadButton = document.querySelector('button#play');
downloadButton.addEventListener('click', () => {
  recordButton.disabled = true;
  const blob = new Blob(recordedBlobs, {type: 'video/webm'});
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  // a.href = url;
  // a.download = 'test.webm';
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }, 100);
  uploadBlob(blob);
  recordButton.disabled = false;
});

function handleSourceOpen(event) {
  console.log('MediaSource opened');
  sourceBuffer = mediaSource.addSourceBuffer('video/webm; codecs="vp8"');
  console.log('Source buffer: ', sourceBuffer);
}

function handleDataAvailable(event) {
  if (event.data && event.data.size > 0) {
    recordedBlobs.push(event.data);
  }
}

function startRecording() {
  recordedBlobs = [];
  let options = {mimeType: 'video/webm;codecs=vp9'};
  if (!MediaRecorder.isTypeSupported(options.mimeType)) {
    console.error(`${options.mimeType} is not Supported`);
    //errorMsgElement.innerHTML = `${options.mimeType} is not Supported`;
    options = {mimeType: 'video/webm;codecs=vp8'};
    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
      console.error(`${options.mimeType} is not Supported`);
      //errorMsgElement.innerHTML = `${options.mimeType} is not Supported`;
      options = {mimeType: 'video/webm'};
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        console.error(`${options.mimeType} is not Supported`);
        //errorMsgElement.innerHTML = `${options.mimeType} is not Supported`;
        options = {mimeType: ''};
      }
    }
  }

  try {
    mediaRecorder = new MediaRecorder(window.stream, options);
  } catch (e) {
    console.error('Exception while creating MediaRecorder:', e);
    //errorMsgElement.innerHTML = `Exception while creating MediaRecorder: ${JSON.stringify(e)}`;
    return;
  }

  console.log('Created MediaRecorder', mediaRecorder, 'with options', options);
  recordButton.textContent = 'STOP';
  // toggle visibility
  //document.getElementById("record-icon").style.display = "none";

  //playButton.disabled = true;
  downloadButton.disabled = true;
  mediaRecorder.onstop = (event) => {
    console.log('Recorder stopped: ', event);
  };
  mediaRecorder.ondataavailable = handleDataAvailable;
  mediaRecorder.start(10); // collect 10ms of data
  console.log('MediaRecorder started', mediaRecorder);
}

function stopRecording() {
  mediaRecorder.stop();
  console.log('Recorded Blobs: ', recordedBlobs);
}

function handleSuccess(stream) {
  recordButton.disabled = false;
  console.log('getUserMedia() got stream:', stream);
  window.stream = stream;

  const gumVideo = document.querySelector('video#gum');
  gumVideo.srcObject = stream;

}

async function init(constraints) {
  try {
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    handleSuccess(stream);
  } catch (e) {
    console.error('navigator.getUserMedia error:', e);
    //errorMsgElement.innerHTML = `navigator.getUserMedia error:${e.toString()}`;
  }
}

$(document).keypress(function(e) {
  if(e.which == 13) {
    console.log("keypressed");
    window.location.href = "/slideshow";
    //console.log("{{ url_for('video') }}");
  }
});

function uploadBlob(blob) {
    var formData = new FormData();
    formData.append('file', blob);
    $.ajax({
        url: '/video/upload',
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            //alert('Successfully uploaded.');
        },
        error: function(jqXHR, textStatus, errorMessage) {
            //alert('Error:' + JSON.stringify(errorMessage));
        }
    });

}

$( document ).ready(function() {
    window.setInterval(shouldCameraViewBeDeactivated, 100);
});

function shouldCameraViewBeDeactivated() {
    $.post("/shouldCameraBeDeactivated",
        {},
        function (response) {
            if (response === "No") {
                // The server has no file for us to display
                //console.log("Server says no new update.");
            } else {
                // TODO Should the grandparent be given the option to save the video first? For demo, no
                let redirect = "http://127.0.0.1:5001/slideshow";
                window.location.href = redirect;
            }
        },
        "text");
}

// convert the touch input to map to the button
// for mapping the input on touch screen
var container = document.querySelector("#container");

// retrieve left button and write button

container.addEventListener("click", getClickPosition, false);

function getClickPosition(e) {
    var xPosition = e.clientX;
    var yPosition = e.clientY;
    console.log(xPosition, yPosition);
    if (yPosition < 480/2 - 30) {
      console.log('right button clicked');
      // click the right button
      downloadButton.click();
      // downloadButton.disabled = true;
    } else if (yPosition > 480/2 + 30){
      console.log('left button clicked');
      // click the left button
      recordButton.click();
    }
}
