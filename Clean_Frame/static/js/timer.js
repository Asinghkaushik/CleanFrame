$(document).ready(function() {
    $('#message').fadeIn('slow', function() {
        $('#message').delay(4000).fadeOut(4000);
    });
    document.getElementById("resend_ootp").disabled = true;
    setTimeout(function() { document.getElementById("resend_ootp").disabled = false; }, 5000);
});