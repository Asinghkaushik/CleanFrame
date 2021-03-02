// $(document).ready(function () {
// 	$('#choose-file').change(function () {
// 		var i = $(this).prev('label').clone();
// 		var file = $('#choose-file')[0].files[0].name;
// 		$(this).prev('label').text(file);
// 	});
//  });
$(document).ready(function(){
	$('.js-edit, .js-save').on('click', function(){
  	var $form = $(this).closest('form');
  	$form.toggleClass('is-readonly is-editing');
    var isReadonly  = $form.hasClass('is-readonly');
    $form.find('input,textarea').prop('disabled', isReadonly);
		$form.find('select').prop('disabled', isReadonly);
    $form.find('input,file').prop('disabled', isReadonly);
  });
});
$(document).ready(function(){
	$('#div_img, #img_js_save').on('click', function(){
  	var $form = $(this).closest('form');
  	$form.toggleClass('is-readonly is-editing');
    var isReadonly  = $form.hasClass('is-readonly');
    $form.find('input,file').prop('disabled', isReadonly);
  });
});
function validate_company_profile_2(){
	if(document.getElementById("company_name").value.length <= 0){
		alert("Company Name can not be empty.")
		return false
	}
	if(document.getElementById("address").value.length <= 0){
		alert("Company Address can not be empty.")
		return false
	}
	if(document.getElementById("duration").value.length <= 0){
		alert("Internship Duration can not be empty.")
		return false
	}
	if(document.getElementById("number_of_students").value.length <= 0){
		alert("Number of students can not be empty.")
		return false
	}
	if(document.getElementById("internship_position").value.length <= 0){
		alert("Internship Position can not be empty.")
		return false
	}
	cgpa = document.getElementById("minimum_cgpa").value
	if(validate_cgpa(cgpa)==false){
		alert("CGPA is not in proper format.")
		return false
	}
	stipend = document.getElementById("stipend").value
	if(validate_float(stipend)==false){
		alert("Stipend is not in proper format.")
		return false
	}
	return true
}

function validate_float(str){
	if (str.match(/^(?=.+)(?:[1-9]\d*|0)?(?:\.\d+)?$/))
	  return true;
	return false;

}
function validate_cgpa(str){
	if (str.match(/^(10|\d)(\.\d{1,2})?$/))
	  	return true;
	return false;
}

$(document).ready(function(){
	link=document.getElementById("my_cv").innerHTML
	myname=link.substring(11,link.length)
	document.getElementById("my_cv").innerHTML=myname
});