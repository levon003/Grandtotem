var video = document.getElementById("myVideo");
var duration = Infinity;

if (video !== null) {
  video.onclick = function () {
    video.play();
    //console.log(video.duration);
  }
  window.setInterval(function(t){
    if (video.readyState > 0) {
      duration = video.duration;
      console.log(video.duration);
      clearInterval(t);
    }
    if (duration === Infinity) {
      // do nothing
    } else {
      // Your application has indicated there's an error
      window.setTimeout(function(){
      // Move to a new location or you can do something else
      window.location.href = "/slideshow";
    }, (duration*1000+3000));
    }
  },500);
} else {
    // Your application has indicated there's an error
    window.setTimeout(function(){
    // Move to a new location or you can do something else
    window.location.href = "/slideshow";
  }, (10000));
}
