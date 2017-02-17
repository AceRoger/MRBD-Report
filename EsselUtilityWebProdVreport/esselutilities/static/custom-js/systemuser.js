//function for active tab behind model


$(function() {
    $(".active-me").removeClass("active");
    $('#system_user_menu').addClass("active");
});

//Js for show active tab
$(document).ready(function() {

    $('a[data-toggle="tab"]').on('show.bs.tab', function(e) {
        localStorage.setItem('activeTab', $(e.target).attr('href'));
    });
    var activeTab = localStorage.getItem('activeTab');
    if (activeTab) {
        $('#myTab a[href="' + activeTab + '"]').tab('show');
    }
});

//Jquery Validation For Add Mr
$(function() {
    $('#frmAddMr').validate({
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
});

//jQuery Validation for Edit Approvar
$(function() {
    $('label.error').hide();
    $('#frmEditApproval').validate({
        rules: {
            Fname: "required",
            Lname: "required",
            Approvpassword: {
                required: true,
                minlength: 6
            },
            ApprovretypePassword: {
                required: true,
                minlength: 6,
                equalTo: Approvpassword
            }
        },
        messages: {
            Fname: "First Name is required",
            Lname: "Last Name is required",
            Approvpassword: "Password length more than 6 character",
            ApprovretypePassword: "Retype Password same as Password ",
        }
    });
});

//Jquery Valiadation Add Validator
$(function() {
    $('#frmAddValidator').validate({
        rules: {
            firstName: "required",
            lastName: "required",
            employeeId: "required",
            mrIMEI: "required",
            emailID: {
                required: true,
                email: true
            },
            valPassword: {
                required: true,
                minlength: 6
            },
            valretypePassword: {
                required: true,
                minlength: 6,
                equalTo: valPassword
            },
        },
        messages: {
            firstName: "First Name is required",
            lastName: "Last Name is required",
            employeeId: "Please enter  employee id",
            emailID: "Email is not entered in correct format",
            valPassword: "Password length more than 6 character",
            valretypePassword: "Retype Password same as Password ",

        }
    });
});


//jquery validation for add admin
$(function() {
    $('#frmAddAdmin').validate({
        rules: {
            firstName: "required",
            lastName: "required",
            employeeId: "required",
            mrIMEI: "required",
            role: "required",

            emailID: {
                required: true,
                email: true
            },
            adminPassword: {
                required: true,
                minlength: 6
            },
            adminretypePassword: {
                required: true,
                minlength: 6,
                equalTo: adminPassword
            }

        },
        messages: {
            firstName: "First Name is required",
            lastName: "Last Name is required",
            employeeId: "Please enter  employee id",
            role: "Role is required",
            emailID: "Email is not entered in correct format",
            adminPassword: "Password length more than 6 character",
            adminretypePassword: "Retype Password same as Password ",
        }
    });
});


//open Add Mr Form
function openAddMrFrm() {
    $('#frmAddMr').trigger("reset");
    $('label.error').hide();
    $('#addmr').modal('show');

}

function openExcel() {
    $('#frmOpenExcel').trigger("reset");
    $('label.error').hide();
    $('#excelOpen').modal('show');
}


//open Add Validator Form
function openAddValidatorFrm() {
    $('#frmAddValidator').trigger("reset");
    $('label.error').hide();
    $('#validator').modal('show');

}

//open Add Admin Form
function openAddAdminFrm() {
    $('#frmAddAdmin').trigger("reset");
    $('label.error').hide();
    $('#admin').modal('show');

}


//function openEditApprvalFrm() {
//    $('#frmEditApproval').trigger("reset");
//    $('label.error').hide();
//    $('#editApproval').modal('show');
//
//}


function openEditApprvalFrm(id){
$("#editApproval").modal('show');
$('label.error').hide();

$.ajax({
        type: "GET",
        url: '/meterreader/view-edit-approval/',
        data: {
            'app_id': id
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                $('#txt_roleId').val(response.data1.userRole);
                $('#Fname').val(response.data1.Fname);
                $('#Lname').val(response.data1.Lname);
                $('#ApprovemailID').val(response.data1.ApprovemailID);
                $('#phone').val(response.data1.phone);
                $('#days').val(response.data2.days);

            }
        },
        error: function(response) {
            bootbox.alert("<span class='center-block text-center'>Data is not save!</span>");
        },
        beforeSend: function() {
        $("#processing").show();
        },
        complete: function() {
        $("#processing").hide();
        }
    });
}

// Search Function for meter Reader by name
$("#searchTxt").keyup(function() {

    $(".fbbox").each(function() {
        var count = ($(this).attr("id")).toLowerCase();
        if (count.indexOf(($("#searchTxt").val()).toLowerCase()) !== -1)
            $(this).show();
        else
            $(this).hide();
    });
});

// Search Function for Validator by name
$("#searchValidator").keyup(function() {
    $(".fbbox2").each(function() {
        var count = ($(this).attr("id")).toLowerCase();
        if (count.indexOf(($("#searchValidator").val()).toLowerCase()) !== -1)
            $(this).show();
        else
            $(this).hide();
    });
});
// Search Function for Validator by name
$("#searchAdmin").keyup(function() {
    $(".fbbox3").each(function() {
        var count = ($(this).attr("id")).toLowerCase();
        if (count.indexOf(($("#searchAdmin").val()).toLowerCase()) !== -1)

            $(this).show();
        else
            $(this).hide();
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

    //Save Meter Reader Data
    $("#btn_save").click(function() {
        check_flag = true
        $("#frmAddMr input").each(function(index, value) {
            if (value.checkValidity() == false) {
                check_flag = false
                $("#mr_submit_btn1").click();
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
            $("#mr_submit_btn1").click();
            return false
        } else {
            $.ajax({
                type: "POST",
                //url:'/appname/function call
                url: '/meterreader/save-mr/',
                //data:$ form id
                data: $('#frmAddMr').serialize(),
                success: function(response) {
                    if (response.success == "true") {
                    $('#addmr').modal('hide');
                    bootbox.alert("<span class='center-block text-center'>Successfully data has been save!</span>",function(){
                    location.reload();
                    });
                }  else if (response.success == "mridexist") {
                         toastr.error("<span class ='center-block text-center'>Employee Id is already Exist Can't Save!</span>");
                    } else if (response.success == "mremailexist") {
                         toastr.error("<span class ='center-block text-center'>Email Id is already Exist Can't Save!</span>");
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

// change user status
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
//                    console.log(response);
//                    console.log( $('#'+response.user_id).val())
                    $('#'+response.user_id).prop('checked', true);
//                    console.log( $('#'+response.user_id).val())
//                    location.reload();
                    }
                else
                    bootbox.alert("<span class ='center-block text-center'>Server Error Please Contact Server Admin</span>",function(){location.reload();});

            },
            error: function(response) {
                toastr.error("Error!");
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

function changeStatus() {

    console.log($(this).state);
}

    //Save Validator data
    $("#validator_save").click(function() {
        check_flag = true
        $("#frmAddValidator input").each(function(index, value) {
            if (value.checkValidity() == false) {
                check_flag = false
                $("#validator_submit_btn").click();
                return false
            } else {
                check_flag = true
            }
        });
        if ($("#password").val() != $("#retypePassword").val()) {
            $("#divCheckPasswordMatch2");
            return false
        } else {
            $("#divCheckPasswordMatch2").html('');
        }

        if (check_flag == false) {
            $("#validator_submit_btn").click();
            return false
        } else {
            $.ajax({
                type: "POST",
                url: '/meterreader/save-validator/',
                data: $('#frmAddValidator').serialize(),
                success: function(response) {
                  if (response.success == "true") {
                    $('#validator').modal('hide');
                    bootbox.alert("<span class='center-block text-center'>Successfully data has been save!</span>",function(){
                    location.reload();
                    });
                } else if (response.success == "idexist") {
                        toastr.error("<span class ='center-block text-center'>Employee Id is already Exist Can't Save!</span>");
                    } else if (response.success == "emailexist") {
                          toastr.error("<span class ='center-block text-center'>Email Id is already Exist Can't Save!</span>");
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





//js for opening the calender in javascript
$(function() {
    $("#Approvpassword").attr("disabled", "disabled");
    $("#ApprovretypePassword").attr("disabled", "disabled");


});
$('#changePwd').change(function() {
    change_password_change_status();
});

function change_password_change_status() {
    if ($('#changePwd').is(":checked")) {
        $("#check_pwdchange_status").val('change_password');
        $("#Approvpassword").removeAttr("disabled");
        $("#ApprovretypePassword").removeAttr("disabled");
    } else {
        $("#check_pwdchange_status").val('donotchange_password');
        $("changePwd").text('change_password');
        $("#Approvpassword").attr("disabled", "disabled");
        $("#ApprovretypePassword").attr("disabled", "disabled");
    }
}



// save edit model Approval model save into databases
$("#approval_save").click(function() {
    check_flag = true
    $("#frmEditApproval input").each(function(index, value) {
        if (value.checkValidity() == false) {
            check_flag = false
            $("#approvar_submit_btn").click();
            return false
        } else {
            check_flag = true
        }
    });


    if ($("#Approvpassword").val() != $("#ApprovretypePassword").val()) {
        $("#divCheckPasswordMatch4");
        return false
    } else {
        $("#divCheckPasswordMatch4").html('');
    }
    if (check_flag == false) {
        $("#approvar_submit_btn").click();
        return false
    } else {
        $.ajax({
            type: "POST",
            url: '/meterreader/edit-save-approver/',
            data: $('#frmEditApproval').serialize(),
            success: function(response) {
                console.log('response', response);
               if (response.success == "true") {
                    $('#editDetail').modal('hide');
                    bootbox.alert("<span class='center-block text-center'>Successfully data has been save!</span>",function(){
                    location.reload();
                    });
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

    //Save admin data
    $("#admin_save").click(function() {
        check_flag = true
        $("#frmAddAdmin input").each(function(index, value) {
            if (value.checkValidity() == false) {
                check_flag = false
                $("#admin_submit_btn").click();
                return false
            } else {
                check_flag = true
            }
        });
        if ($("#password").val() != $("#retypePassword").val()) {
            $("#divCheckPasswordMatch3");
            return false
        } else {
            $("#divCheckPasswordMatch3").html('');
        }

        if (check_flag == false) {
            $("#admin_submit_btn").click();
            return false
        } else {
            $.ajax({
                type: "POST",
                url: '/meterreader/save-admin/',
                data: $('#frmAddAdmin').serialize(),
                success: function(response) {
                    if (response.success == "true") {
                    $('#admin').modal('hide');
                    bootbox.alert("<span class='center-block text-center'>Successfully data has been save!</span>",function(){
                    location.reload();
                    });
                } else if (response.success == "adminidexist") {
                         toastr.error("<span class ='center-block text-center'>Employee Id is already Exist Can't Save!</span>");
                    } else if (response.success == "adminemailexist") {
                          toastr.error("<span class ='center-block text-center'>Email Id is already Exist Can't Save!</span>");
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


$('.datepickerDate1').datepicker({
    format: 'dd/mm/yyyy',
    minDate: 1,
    startDate:'-6m',
    autoclose: true
});


$('.newdatepickerDate').datepicker({
    format: "dd/mm/yyyy",
    autoclose: false,
    changeMonth: true,
    changeYear: true,
    yearRange: "-100:+0",
});

//
//$("#monthYear").change(function(){
//    monthYear=$("#monthYear").val()
//
//    url = "/meterreader/open-systemuser-index/"+ monthYear;
//    window.location.href = url;
//});

function excel() {
     //$.trim(fit_start_time);
     //$.trim(fit_end_time);

     var fit_start_time = $.trim($("#fromDate").val());
     console.log('fdsfkj'+fit_start_time+'kjjjjkj')
     var fit_end_time  = $.trim($("#toDate").val());



     fit_start_time=fit_start_time.split("/");
     fit_end_time=fit_end_time.split("/");


     st_dt=new Date(fit_start_time[2],fit_start_time[1]-1,fit_start_time[0])
     ed_dt=new Date(fit_end_time[2],fit_end_time[1]-1,fit_end_time[0])

         if ((fit_start_time == "") || (fit_end_time == "")){
            bootbox.alert("Please Enter Valid Date");
             return false;
         }

        if( st_dt > ed_dt ){
            bootbox.alert("Please ensure that the <b>TO Date</b> is greater than or equal to the <b>From Date</b>.");
            check_flag = false
            return false;
        }

    var formData = new FormData();

    chkmode = $("input[name='chkavailable']:checked").val()
    formData.append("chkmode", chkmode);
    formData.append("fromDate", $("#fromDate").val());
    formData.append("toDate", $("#toDate").val());

fromdate=$('#fromDate').val()
todate=$('#toDate').val()

window.location="/meterreader/reading-export-to-excel-systemuser/?fromdate="+fromdate+"&todate="+todate
$("#excelOpen").modal('hide');
}

function refresh() {
        current_month=$("#currentmonth").val()
        $.ajax({
            type: "POST",
           url: '/meterreader/refreshmrinfo/',
            data:{
                'current_month':current_month,

                },

            success: function(response) {
                window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;

            },
            error: function(response) {
                bootbox.alert("An unexpected error occured!");
            },
             beforeSend: function() {
                    $("#processing").show();
             },
             complete: function() {
                    $("#processing").hide();
             }
        });

}

