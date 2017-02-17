//open Edit meterreader Form
function openEditMeterreaderFrm() {
    $('#frmEditMr').trigger("reset");
    $('#editDetail').modal('show');

}


//open Edit meterreader Form
function openEditMeterreaderFrm() {
    $('#frmEditMr')
    $('#editDetail').modal('show');
    $('label.error').hide();//hide the error msg that shown on the model
    $('#frmEditMr').trigger("reset").validate({
        rules: {
            firstName: "required",
            lastName: "required",
            employeeId: "required",
            mrIMEI: "required",
            contactNo: {
                required: true,
                number: true
            },
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
            password: "Password length more than 6 character",
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


//function for checked box
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
    $("#date").hide();
    console.log($('#ntavailable').is(":checked"))
    if ($('#ntavailable').is(":checked")) {
        $('#date').show();
    }

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
            bootbox.alert("Please ensure that the <b>End Date</b> is greater than or equal to the <b>Start Date</b>.");
            check_flag = false
            return false;
        }

    var formData = new FormData();

    chkmode = $("input[name='chkavailable']:checked").val()
    formData.append("chkmode", chkmode);
    formData.append("startDate", $("#startDate").val());
    formData.append("endDate", $("#endDate").val());
    formData.append("mr_id", $("#mr_id").val());

    $.ajax({
        type: "POST",
        url: '/meterreader/update-availability/',
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
    getRoute('#billCycleOne', '#routeDetailOne');
    getRoute('#billCycleTwo', '#routeDetailTwo');
    getRoute('#billCycleThree', '#routeDetailThree');
    getRoute('#billCycleFour', '#routeDetailFour');


// Change user status
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


//function for change route according to bill cycle
$('#billCycleOne').change(function() {
    getRoute('#billCycleOne', '#routeDetailOne');
});

$('#billCycleTwo').change(function() {
    getRoute('#billCycleTwo', '#routeDetailTwo');
});
$('#billCycleThree').change(function() {
    getRoute('#billCycleThree', '#routeDetailThree');
});
$('#billCycleFour').change(function() {
    getRoute('#billCycleFour', '#routeDetailFour');
});

function getRoute(billCycleDropDown, routeDropDown) {
    id = $(billCycleDropDown).val();
    $.ajax({
        type: 'POST',
        url: '/meterreader/get-route/',
        data: {
            'bill_cycle_code': id
        },
        success: function(response) {
            console.log('response', response);
            $(routeDropDown).html('');
            $.each(response.route_list, function(index, item) {
                $(routeDropDown).append(item);
            });
        },
        error: function(response) {
            alert("Error!");
        },
    });
}

//$(document).ready(function() {
//    // enter keyd
//    $(document).bind('keypress', function(e) {
//        if (e.keyCode == 13) {
//            $('#btn_save').trigger('click');
//        }
//    });

    //save edit meterreader detail into database
    $("#btn_save").click(function() {
        check_flag = true
        $("#frmEditMr input").each(function(index, value) {
            if (value.checkValidity() == false) {
                check_flag = false
                $("#edit_meterreader_submit").click();
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
        if (check_flag == false) {
            $("#edit_meterreader_submit").click();
            return false
        } else {
            $.ajax({
                type: "POST",
                url: '/meterreader/edit-save-mr/',
                data: $('#frmEditMr').serialize(),
                success: function(response) {
                    console.log('response', response);
                      if (response.success == "true") {
                    $('#editDetail').modal('hide');
                    bootbox.alert("<span class='center-block text-center'>Successfully data has been save!</span>",function(){
                    location.reload();
                    });
                }  else if (response.success == "exist") {
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
    mr_id = $("#mr_id").val()
    url = "/meterreader/detail-mr/"+ mr_id +"/"+ monthYear;
    window.location.href = url;
});





