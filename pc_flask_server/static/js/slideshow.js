$(document).keypress(function(e) {
  if(e.which == 13) {
    console.log("keypressed");
    window.location.href = "/video";
    //console.log("{{ url_for('video') }}");
  }
  if(e.which == 32) {
    var file_name = {file_name: '6.jpg'}
    $.ajax({
        url: '/slideshow/view',
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
            window.location.href = "/slideshow/view";
        }
    });

  }
});
