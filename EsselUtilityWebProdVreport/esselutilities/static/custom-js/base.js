
$(document).ready(function(){
    if($("#messageid1").val() == 1){
        toastr.info($("#messagename1").val());
    }

});

$(function() {
    var dataTable = $('#bill').dataTable(
    );
});
function changedPassword() {
    $('label.error').hide();
    $('#changedpassword').modal('show');
    $('#changedpwdFrm').trigger("reset");
    }


$(function() {
    $('#changedpwdFrm').validate({
        rules: {
            oldpw: {
                required: true,
            },
            newpwd: {
                required: true,
                minlength: 6
            },
             retypepwd: {
                required: true,
                minlength: 6,
                equalTo: newpwd
            }
        },
        messages: {
            oldpw: "Please enter valid old password",
            newpwd: {
            required: "Please enter new password ",
            minlength: "Your password must be at least 6 characters long"
            },
            retypepwd: {
            required: "Retype password same as new password ",
            minlength: "Your password must be at least 6 characters long"
            },
        }
    });
});

$("#submitbtn").click(function() {
$("#changedpwdFrm input").each(function(index, value) {
        if (value.checkValidity() == false) {
            check_flag = false
            return false;
        } else {
            check_flag = true
        }
    });
    if (check_flag == false) {
        $("#pass_btn").click();
        return false
    } else {
        $.ajax({
            type: "POST",
            url: '/authen/changepassword/',
            data: $('#changedpwdFrm').serialize(),
            success: function(response) {
                    if (response.success == "true") {
                      bootbox.alert(response.message);
                      $('#changedpassword').modal('hide')
                    }else if (response.success == "false"){
                      $('#changedpassword').modal('show')
                      bootbox.alert(response.message);
                    }
                    else if(response.success == "samepwd"){
                    bootbox.alert(response.message);
                    }
                    else if(response.success == "blank"){
                    bootbox.alert(response.message);
                    }
                 },
            error: function(response) {
               bootbox.alert('Password is not changed !');
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