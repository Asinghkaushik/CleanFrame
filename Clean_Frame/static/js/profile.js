function validate_number() {
    var number = document.getElementById("contact_number").value;
    if (number.length != 10) {
        alert("Invalid Phone Number entered")
        return false;
    }
    document.getElementById("mybutton").disabled = true;
    return true;
}

function disable_button() {
    document.getElementById("mybutton").disabled = true;
    return true;
}