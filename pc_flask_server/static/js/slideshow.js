$(document).keypress(function(e) {
  if(e.which == 13) {
    console.log("keypressed");
    window.location.href = "/video";
    //console.log("{{ url_for('video') }}");
  }
  if(e.which == 32) {
    var file_name = {file_name: '6.jpg'}
    $.ajax({
        url: '/slideshow',
        type: "POST",
        dataType: 'json',
        data: JSON.stringify(file_name),
        processData: false,
        contentType: false,
        success: function(response) {
            console.log("reload");
        },
        error: function(jqXHR, textStatus, errorMessage) {
            //alert('Error:' + JSON.stringify(errorMessage));
        },
        complete: function(data) {
            redirect = "http://127.0.0.1:5001/view?selected=6.jpg"
            window.location.href = redirect;
        }
    });

  }
});
