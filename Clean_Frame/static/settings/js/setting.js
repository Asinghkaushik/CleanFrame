function check_ok() {
    var answer = confirm("Are you sure to delete your account?")
    if (answer) {
        return true;
    }
    return false;
}