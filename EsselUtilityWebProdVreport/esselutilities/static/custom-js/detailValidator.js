//open Edit Validator Form


function openEditValidatorFrm(){
    $('#frmEditValidator').trigger("reset");
    $('#editDetail').modal('show');
}

//open Edit meterreader Form
function openEditValidatorFrm() {
    $('#frmEditValidator')
    $('#editDetail').modal('show');
    $('label.error').hide();
    $('#frmEditValidator').trigger("reset").validate({
        rules: {
            firstName: "required",
            lastName: "required",
            employeeId: "required",
            mrIMEI: "required",

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
        messages: {
            firstName: "First Name is required",
            lastName: "Last Name is required",
            employeeId: "Please enter  employee id",
            contactNo: "Number is not entered in correct format",
            emailID: "Email is not entered in correct format",
            password: "Password should be more than 6 character",
            retypePassword: "Retype Password same as Password ",
            mrIMEI: "Please enter valid IMEI number"
        }
    });
}


//js for opening the calender in javascript
$(function() {

    $('#startDate').datepicker({
        format: 'dd/mm/yyyy',
        minDate: 1,
        startDate: 'd',
        autoclose: true
    });

    $('#endDate').datepicker({
        format: 'dd/mm/yyyy',
        minDate: 1,
        startDate: 'd',
        autoclose: true
    });

    $("#password").attr("disabled", "disabled");
    $("#retypePassword").attr("disabled", "disabled");

});
$('#changePwd').change(function() {
    change_password_change_status();
});

function change_password_change_status() {
    if ($('#changePwd').is(":checked")) {
        $("#check_pwdchange_status").val('change_password');
        $("#password").removeAttr("disabled");
        $("#retypePassword").removeAttr("disabled");
    } else {
        $("#check_pwdchange_status").val('donotchange_password');
        $("changePwd").text('change_password');
        $("#password").attr("disabled", "disabled");
        $("#retypePassword").attr("disabled", "disabled");
    }
}



//function for radio button
$(function() {
    $("#startDate").val('');
    $("#endDate").val('');

    $("#date").hide();
    $('input[type="radio"]').click(function() {
        if ($(this).attr('id') == 'ntavailable') {
            $('#date').show();

        } else {
            $('#date').hide();
        }
    });
});


//Save Date function
$("#save_date").click(function() {
     var fit_start_time  = $("#startDate").val();
     var fit_end_time    = $("#endDate").val();

     fit_start_time=fit_start_time.split("/");
     fit_end_time=fit_end_time.split("/");


     st_dt=new Date(fit_start_time[2],fit_start_time[1]-1,fit_start_time[0])
     ed_dt=new Date(fit_end_time[2],fit_end_time[1]-1,fit_end_time[0])


        if( st_dt > ed_dt ){
            bootbox.alert("Please ensure that the <b>End Date</b> is greater than or equal to the Start Date.");
            check_flag = false
            return false;
        }

    var formData = new FormData();

    chkmode = $("input[name='chkavailable']:checked").val()
    formData.append("chkmode", chkmode);
    formData.append("startDate", $("#startDate").val());
    formData.append("endDate", $("#endDate").val());
    formData.append("validatorid2", $("#validatorid2").val());

    $.ajax({
        type: "POST",
        url: '/meterreader/update-validator-availability/',
        data: formData,
        cache: false,
        processData: false,
        contentType: false,

        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                bootbox.alert('Successfully Data Has Been Saved!', function() {
                    location.reload();
                });

            } else("#errorMessage")
        },
        error: function(response) {
            alert('cant save');
        },
        beforeSend: function() {
            $("#processing").show();
        },
        complete: function() {
            $("#processing").hide();
        }
    });
});



$(document).ready(function() {
    $('.user-status').on('switchChange.bootstrapSwitch', function(event, state) {
        console.log(this.id)
        $.ajax({
            type: 'POST',
            url: '/meterreader/change-user-status/',
            data: {
                'user_id': this.id,
                'status': state
            },
           success: function(response) {
            if (response.success == 'true')
                bootbox.alert("<span class ='center-block text-center'>Operation Successful</span>");
           else if (response.success == 'assigned'){
                     bootbox.alert("<span class ='center-block text-center'>User Has Already Assigned Task</span>",function(){location.reload();});
                      $('#'+response.user_id).prop('checked', true);
//                      location.reload();
                      }
           else
                bootbox.alert("<span class ='center-block text-center'>Server Error Please Contact Server Admin</span>",function(){location.reload();});

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



// save edit model save into databases
$("#btn_save").click(function() {

    var check_flag = true
    console.log('before====>')
    console.log(check_flag)

    $("#frmEditValidator input").each(function(index, value) {
        if (value.checkValidity() == false) {
            check_flag = false
            $("#edit_validator_submit").click();
            return false
        } else {
            check_flag = true
        }
    });

    if ($("#password").val() != $("#retypePassword").val()) {
        $("#divCheckPasswordMatch");
        return false
    } else {
        $("#divCheckPasswordMatch").html('');
    }

    console.log('after====>');
    console.log(check_flag);


    if (check_flag == false) {
	console.log('check_flag in false');
	console.log(check_flag);
        $("#edit_validator_submit").click();
        return false
    } else {
    
    console.log('-----------------');
    console.log(check_flag);
        $.ajax({
            type: "POST",
            url: '/meterreader/edit-save-validator/',
            data: $('#frmEditValidator').serialize(),
            success: function(response) {
                console.log('response', response);
               if (response.success == "true") {
                    $('#editDetail').modal('hide');
                    bootbox.alert("<span class='center-block text-center'>Successfully data has been save!</span>",function(){
                    location.reload();
                    });
                } else if (response.success == "exist") {
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




$("#monthYear").change(function(){
    monthYear=$("#monthYear").val()
    validator_id = $("#validator_id").val()
    url = "/meterreader/detail-validator/"+ validator_id +"/"+ monthYear;
    window.location.href = url;
});