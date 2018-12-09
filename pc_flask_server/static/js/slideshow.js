$( document ).ready(function() {
    window.setInterval(intervalFunction, 100);
    console.log (window.innerHeight);
});

function intervalFunction() {
    shouldFileBeDisplayed();
    shouldCameraViewBeActive();
}

function shouldFileBeDisplayed() {
    $.post("/shouldFileBeDisplayed",
        {},
        function (response) {
            if (response === "No") {
                // The server has no file for us to display
                //console.log("Server says no new update.");
            } else {
                let filename = response;
                let redirect = "http://127.0.0.1:5001/view?selected=" + filename;
                console.log(redirect);
                window.location.href = redirect;
            }
        },
        "text");
}

function shouldCameraViewBeActive() {
    $.post("/shouldCameraViewBeActive",
        {},
        function (response) {
            if (response === "No") {
                // The server has no file for us to display
                //console.log("Server says no new update.");
            } else {
                let redirect = "http://127.0.0.1:5001/video";
                window.location.href = redirect;
            }
        },
        "text");
}
