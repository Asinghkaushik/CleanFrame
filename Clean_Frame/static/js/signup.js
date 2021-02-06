function validate() {
    email = document.getElementById('email').value
    var n = email.search('@iiita.ac.in');
    if (n == -1) {
        document.getElementById("pass_error3").innerHTML = "";
        document.getElementById("pass_error4").innerHTML = "";
        document.getElementById("pass_error2").innerHTML = "";
        document.getElementById("pass_error1").innerHTML = "";
        document.getElementById("email_error").innerHTML = "Email entered is not associated with IIITA";
        return false;
    }
    if (email.length >= 25)
        return false;
    password1 = document.getElementById('password3').value
    password2 = document.getElementById('password4').value
    if (password1 != password2) {
        document.getElementById("email_error").innerHTML = "";
        document.getElementById("pass_error4").innerHTML = "";
        document.getElementById("pass_error2").innerHTML = "";
        document.getElementById("pass_error1").innerHTML = "";
        document.getElementById("pass_error3").innerHTML = "Both the passwords are diferent";
        return false;
    } else {
        var val = passwordchecker(password1)
        if (!val) {
            document.getElementById("email_error").innerHTML = "";
            document.getElementById("pass_error3").innerHTML = "";
            document.getElementById("pass_error2").innerHTML = "";
            document.getElementById("pass_error1").innerHTML = "";
            document.getElementById("pass_error4").innerHTML = "Password length must be min 8 with digits and special characters";
            return false
        }
        return true
    }
}

function validate_passwords_new() {
    password1 = document.getElementById('password3').value
    password2 = document.getElementById('password4').value
    if (password1 != password2) {
        alert("Both the passwords are diferent")
        return false;
    } else {
        var val = passwordchecker(password1)
        if (!val) {
            alert("Not a valid password format, password must be of format:\nAt least 1 uppercase character.\nAt least 1 lowercase character.\nAt least 1 digit.\nAt least 1 special character.\nMinimum 8 characters.")
            return false
        }
        return true
    }
}

function validate_passwords() {
    password1 = document.getElementById('password1').value
    password2 = document.getElementById('password2').value
    if (password1 != password2) {
        document.getElementById("email_error").innerHTML = "";
        document.getElementById("pass_error3").innerHTML = "";
        document.getElementById("pass_error4").innerHTML = "";
        document.getElementById("pass_error2").innerHTML = "";
        document.getElementById("pass_error1").innerHTML = "Both the passwords are diferent";
        return false;
    } else {
        var val = passwordchecker(password1)
        if (!val) {
            document.getElementById("email_error").innerHTML = "";
            document.getElementById("pass_error3").innerHTML = "";
            document.getElementById("pass_error4").innerHTML = "";
            document.getElementById("pass_error1").innerHTML = "";
            document.getElementById("pass_error2").innerHTML = "Password length must be min 8 with digits and special characters";
            return false
        }
        return true
    }
}

function passwordchecker(str) {
    if (str.match(/[a-z]/g) && str.match(
            /[A-Z]/g) && str.match(
            /[0-9]/g) && str.match(
            /[^a-zA-Z\d]/g) && str.length >= 8)
        return true;
    return false;
}