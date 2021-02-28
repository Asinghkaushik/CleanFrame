<<<<<<< HEAD
// function set_class(id){
//   document.getElementById(id).className += " active";
// }
document.getElementById("first").addEventListener("click", function() {
  document.getElementById("first").classList.add('active');
  $(".sidebar").on("click", function(e) {
        e.preventDefault();
        $("body").toggleClass("sb-sidenav-toggled");
    });
});
=======
// function set_class(id){
//   document.getElementById(id).className += " active";
// }
document.getElementById("first").addEventListener("click", function() {
  document.getElementById("first").classList.add('active');
  $(".sidebar").on("click", function(e) {
        e.preventDefault();
        $("body").toggleClass("sb-sidenav-toggled");
    });
});
>>>>>>> 39f439f2208e050483962b024e98da5d42e38482
