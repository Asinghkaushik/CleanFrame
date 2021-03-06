
$(document).ready(function(){
	var element = document.getElementById("main1");
	var positioninfo = element.getBoundingClientRect();
	var width = positioninfo.width;
	var element1 = document.getElementById("cr1");
	var positioninfo1 = element1.getBoundingClientRect();
	var width1 = positioninfo1.width;
	var req_w = (width - width1)*(0.45);
	var e = width1 - 40;
	$('#f1').css('width', e + 'px');
	// $('.my_table').css('width', e + 'px');
	// $('.my_table tr').css('width', e + 'px !important');
	// $('.my_table tbody').css('width', e + 'px !important');
	// $('.input-field').css('width', e + 'px');
	var f2=(e-200)/2;
	$('.profile_save_changes_btn').css('margin-left', f2 + 'px');
	$('.cards_form').css('margin-left', req_w + 'px');
	$('.cards_form').css('margin-right', req_w + 'px');
});
$(document).ready(function(){
	var element = document.getElementById("main1");
	var positioninfo = element.getBoundingClientRect();
	var width = positioninfo.width;
	var element1 = document.getElementById("cr1");
	var positioninfo1 = element1.getBoundingClientRect();
	var width1 = positioninfo1.width;
	var req_w = (width - width1)*(0.4);
	var e = width1 - 40;
	$('.comp_form').css('width', e + 'px');
	$('.comp_table').css('width', e + 'px');
	var f2=(e-200)/2;
	var f3=(e-130)/2;
	$('.profile_save_changes_btn').css('margin-left', f2 + 'px');
	$('.profile_save_changes_btn1').css('margin-left', f3 + 'px');
	$('.cards_form_comp').css('margin-left', req_w + 'px');
	$('.cards_form_comp').css('margin-right', req_w + 'px');
});
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
