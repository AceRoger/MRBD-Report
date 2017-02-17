
$(document).ready(function(){

$(".active-me").removeClass("active");
$('#dashboard_menu').addClass("active");


$(window).resize(function() {

$('#content').css('height', (window.innerHeight*0.6));

});

$('#content').css('height', (window.innerHeight*0.6));


	$("input").focus(function() {
		$(this).parent().addClass("curFocus")
	});
	$("input").blur(function() {
		$(this).parent().removeClass("curFocus")
	});
});

$(function (){
// $('#login_form').validate({
//        rules:{
//
//            username: {
//                required: true,
//                email: true
//            },
//            password: "required",
//
//        },
//        messages:{
//
//            username: "Please enter valid email id",
//            password: "Please enter valid password",
//        }
//    });

$('#forget_form').validate({
        rules:{

           email: {
                required: true,
                email: true
            },
        },
        messages:{

            email: "Please enter valid email id",
        }
    });



$('#resetpwd_form').validate({
        rules:{
               password: {
                required: true,
                minlength: 6
            },
            confirmpassword: {
                required: true,
                minlength: 6
            }
        },
        messages:{
            password: "Password should be six or more character",
            confirmpassword:"comfirmPassword should be six or more character "
        }
    });
});




 $(document).ready(function()
    {
        // enter keyd
        $(document).bind('keypress', function(e) {
            if(e.keyCode==13){
                 $('#btn_login').trigger('click');
             }
        });

 $('#btn_login').click(function(event) {

    event.preventDefault();

   username=$("#email").val();
    if(username == '' || username == null ){

        $("#login_modal").modal('show');

        return false;
    }
    pwd = $("#pwd").val();
    if(pwd == '' || pwd == null){
        $("#password").modal('show');
        return false;
    }

    $.ajax({
    type : 'POST',
    url : '/authen/login/',
    data : $("#login_form").serialize(),
        success: function(response) {
            if(response.success=='true'){
                    console.log('response',response)
                  //alert(response.url);
                   window.location.href = response.url;
            }
            if(response.success=='Invalid Username'){
             console.log('response',response)
                $("#login_modal").modal('show');

            }
            if(response.success=='Invalid Password'){
             console.log('response',response)
                $("#password").modal('show');
            }
            if(response.success=='false'){
             console.log('response',response)
                 $("#login_failed").modal('show');
            }
            if(response.success=='5'){
                 $("#role_failed").modal('show');
            }
            if(response.success=='6'){
                 $("#user_type").modal('show');
            }
            if(response.success=='7'){
                 $("#role_status").modal('show');
            }
        },
        error: function(response){
            //location.href="/login/"
            console.log('response',response)
            bootbox.alert("Login Error", function(){
                          location.reload();
                         })
        },
    });
 });
});



$('#forget_form').submit(function(event) {
              event.preventDefault();

   if ($("#forget_form").valid())
    {

    $.ajax({
        type : 'POST',
        url : '/authen/user_exist/',
        data : $("#forget_form").serialize(),
            success: function(response) {
                if(response.success=='true'){
                    //console.log('response',response)
             bootbox.alert("Check Your Email, Password reset link is sent successfully", function(){
                     location.href="/"
                     })
                    }
             },
          error: function(response){
                //location.href="/login/"
                console.log('response',response)
                 bootbox.alert("Please enter valid Username", function(){
                      location.reload();
                     })

       },
        beforeSend: function () {
       $(".modal1").show();
    },
    complete: function () {
        $(".modal1").hide();

         },
       });
    }
    else{
        console.log("Form Invalid");
        return false;
    }

});




$('#resetpwd_form').submit(function(event) {

event.preventDefault();

if ($("#resetpwd_form").valid())
{
$.ajax({
type : 'POST',
url : '/authen/confirm_pwd/',
data : $("#resetpwd_form").serialize(),
    success: function(response) {
        if(response.success=='true'){
                console.log('response',response)
                bootbox.alert("Password Reset Successfully", function(){
             location.href="/"
             })
        }
        else{
         bootbox.alert("Password doesn't match with confirmpassword ", function(){
              location.reload();
             })
        }
 },
error: function(response){
    //location.href="/login/"
    //console.log('response',response)
bootbox.alert("Password doesn't match with confirmpassword", function(){
              location.reload();
             })
},
});

}
else{
  console.log("Form Invalid");
 }

});


$("#monthYear").change(function(){
//alert("hii");
    monthYear=$("#monthYear").val()
    url = "/dashboard/"+ monthYear;
    window.location.href = url;
});







//$(document).ready(function()
//    {
//        // enter keyd
//        $(document).bind('keypress', function(e) {
//            if(e.keyCode==13){
//                 $('#btn_reset').trigger('click');
//             }
//        });
//
//$('#btn_reset').click(function(event) {
//
////alert('test page');
//  event.preventDefault();
//  $.ajax({
//type : 'POST',
//url : '/authen/confirm_pwd/',
//data : $("#resetpwd_form").serialize(),
//    success: function(response) {
//        if(response.success=='true'){
//                console.log('response',response)
//
//              location.href="/"
//              alert("Password Reset Successfully");
//              //console.log('response',response)
//        }
//        else{
//            alert("Enter Password properly");
//        }
//
// },
//error: function(response){
//    //location.href="/login/"
//    console.log('response',response)
//
//},
//});
//
//
//});
//
//
//
//});


//function check_text()
//{
//    emailID=$('#emailID').val()
//    password1=$('#password').val()
//	password2=$('#confirmpassword').val()
//	if(password1==password2)
//	{
//
//				return true;
//
//	}
//	else{
//
//						   return false;
//	}
//
//}
//
//function sendMessage(){
//
//if(check_text()){
//$('#ok-btn').attr('disabled','disabled');
//var formData= new FormData();
//formData.append("emailID",$('#emailID').val());
//
//formData.append("password",$('#password').val());
//formData.append("confirmpassword",$('#confirmpassword').val());
//
//$.ajax({
//type : 'POST',
// url : '/authen/confirm-pwd/',
//data : formData,
//    success: function(response) {
//        if(response.success=='true'){
//                alert('success');
//                //console.log('response',response)
//              location.href="/"
//              //console.log('response',response)
//        }
//        else{
//            alert("Enter Password properly");
//        }
//
// },
//error: function(response){
//    //location.href="/login/"
//    console.log('response',response)
//    alert("Reset Password Failed");
//},
//});
//
//
//});
//}
//}

//$("#monthYear").change(function(){
//    monthYear=$("#monthYear").val()
//    url = "/authen/dashboard/"+ monthYear;
//    window.location.href = url;
//});









