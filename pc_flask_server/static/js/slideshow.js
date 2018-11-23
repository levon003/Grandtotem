$(document).keypress(function(e) {
  if(e.which == 13) {
    console.log("keypressed");
    window.location.href = "/video";
    //console.log("{{ url_for('video') }}");
  }
});
