
//open Edit Validator Form
function openEditAdminFrm(){
    $('#frmEditAdmin').trigger("reset");
    $('#editDetail').modal('show');

}

function openEditAdminFrm(){
    $('#frmEditAdmin')
    $('#editDetail').modal('show');
    $('label.error').hide();
    $('#frmEditAdmin').trigger("reset").validate({
        rules:{
            firstName: "required",
            lastName: "required",
            employeeId: "required",
            role:"required",
            mrIMEI:"required",

            emailID: {
                required: true,
                email: true
            },
             password: {
                required: true,
                minlength: 6
            },
            retypePassword: {
                required: true,
                minlength: 6,
                equalTo: password
            }
        },
        messages:{
            firstName: "First Name is required",
            lastName: "Last Name is required",
            employeeId: "Please  valid employee id",
            role: "Role is required",
            emailID: "Email is not entered in correct format",
            password: "Password should be more than 6 character",
            retypePassword:"Retype Password same as Password ",
            mrIMEI:"Please enter valid IMEI number"
        }
    });
}

$(document).ready(function(){
$('.user-status').on('switchChange.bootstrapSwitch', function(event, state) {
        console.log(this.id)
         $.ajax({
            type: 'POST',
            url: '/meterreader/change-user-status/',
            data: {'user_id':this.id,'status':state },
            success: function(response) {
            if(response.success=='true')
                bootbox.alert("<span class ='center-block text-center'>Operation Successful</span>");
            },
            error: function(response) {
                alert("Error!");
            },
            beforeSend: function() {
        $("#processing").show();
        },
        complete: function() {
         $("#processing").hide();
        }
        });

        });
 });


 $(function(){
   $("#password").attr("disabled", "disabled");
   $("#retypePassword").attr("disabled", "disabled");

     $('#changePwd').change(function() {
     change_password_change_status();
    });
});
function change_password_change_status(){
    if($('#changePwd').is(":checked")) {
            $("#check_pwdchange_status").val('change_password');
    		$("#password").removeAttr("disabled");
            $("#retypePassword").removeAttr("disabled");
    	}
    	else {
    	    $("#check_pwdchange_status").val('donotchange_password');
    	    $("changePwd").text('change_password');
            $("#password").attr("disabled", "disabled");
            $("#retypePassword").attr("disabled", "disabled");
    	}
}

// save edit model save into databases
$("#btn_save").click(function(){
    check_flag = true
    $("#frmEditAdmin input").each(function(index, value) {
        if (value.checkValidity() == false) {
            check_flag = false
            $("#edit_admin_submit").click();
            return false
        } else {
            check_flag = true
        }
    });

    if ($("#password").val() != $("#retypePassword").val()){
            $("#divCheckPasswordMatch").html('');
            return false
        }
        else{
            $("#divCheckPasswordMatch").html('');
        }

    if (check_flag == false) {
        $("#edit_admin_submit").click();
        return false
    }
    else
       {

        $.ajax({
        type: "POST",
        url: '/meterreader/edit-save-admin/',
        data: $('#frmEditAdmin').serialize(),
        success: function(response) {
            console.log('response', response);
              if (response.success == "true") {
                    $('#editDetail').modal('hide');
                    bootbox.alert("<span class='center-block text-center'>Successfully data has been save!</span>",function(){
                    location.reload();
                    });
                }
             else if (response.success == "exist") {
                     toastr.error("<span class ='center-block text-center'>Employee Id is already Exist Can't Save!</span>");
                }
             else("#errorMessage")
        },
        error: function(response) {
            toastr.error('can not save data');
        },
       beforeSend: function() {
        $("#processing").show();
        },
        complete: function() {
         $("#processing").hide();
        }
       });
}
});