
$(function() {
    loadData();
});


function loadData(){
  $('#userTbl').dataTable({
        'destroy': true,
        "ajax": "/admin/list-user/",
        "columns": [{
            "data": "user"
        },{
            "data": "role"
        }, {
            "data": "city"
        }, {
            "data": "status"
        }, {
            "data": "edit"
        }],
    });
}


function viewUser(id) {
            $('#firstName').val('');
            $('#lastName').val('');
            $('#userCity').val('');
            $('#emailId').val('');
            $('#userRole').val('');
            $('#mobileNo').val('');
            $('#employeeId').val('');
    $.ajax({
        type: "GET",
        url: '/admin/view-user/',
        data: {
            'user_id': id
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
            $('#firstName').val(response.user_first_name);
            $('#lastName').val(response.user_last_name);
            $('#userCity').val(response.city_id);
            $('#emailId').val(response.user_email_id);
            $('#userRole').val(response.role_id);
            $('#mobileNo').val(response.user_contact_no);
            $('#employeeId').val(response.employee_id);
            $('#addUserModal').modal('show');
           }
        },
        error: function(response) {

        },
        beforeSend: function() {

        },
        complete: function() {}
    });
}



$("#btn_save").click(function() {

  $("#userFrm input,#userFrm  select").each(function(index, value){
                if(value.checkValidity()==false){
                $("#submit_btn").click();
               }
        });

        if ($("#password").val() != $("#confirmPassword").val()){
            $("#divCheckPasswordMatch").html("Passwords do not match!");
            return false
        }
    $.ajax({
        type: "POST",
        url: '/admin/save-user/',
        data: $('#userFrm').serialize(),
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                alert('Data has been saved!');
            }
        },
        error: function(response) {
            alert('cant save');
        },
        beforeSend: function() {
        },
        complete: function() {
        }
    });
});
