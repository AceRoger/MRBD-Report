$(function(){
    $(".active-me").removeClass("active");
    $('#administrator_menu').addClass("active");
});

$("#searchTxt").keyup(function(){
        $(".testVal").each(function(){
            var count = $(this).attr("id");
            if(count.indexOf($("#searchTxt").val()) !== -1)
                $(this).show();
            else
                $(this).hide();
        });
    });

$( document ).ready(function() {
   get_table_initilize();
});

function viewRoleModal(){
$('label.error').hide();
$('#roleFrm').trigger("reset");
$('.' + 'viewcheckbox').prop("checked", false);
$('.' + 'viewcheckbox').closest('span').removeClass('checked');
$('#addRoleModal').modal('show');
}

/*TODO Ajax call for saving role and there privileges */
$("#saveRoleBtn").click(function() {
var message = $('#roleName').val();
    if (message == "") {
      $("label#roleLabel").show();
      $("#roleName").focus();
      return false;
    }else {
        if ($('div.checkbox-group.required :checkbox:checked').length == 0) {
            $("label#privilegesLabel").show();
            return false;
        }
        $.ajax({
            type: "POST",
            url: '/admin/save-user-role/',
            data: $('#roleFrm').serialize(),
            success: function(response) {
                console.log('response', response);
                if (response.success == "true") {
                    bootbox.alert("<span class='center-block text-center'>Role has been created successfully!</span>");
                    $('#addRoleModal').modal('hide');
                    get_table_initilize();
                }
            },
            error: function(response) {
                bootbox.alert("<span class='center-block text-center'>Role is not create!</span>");
            },
            beforeSend: function() {

            },
            complete: function() {

            }
        });
    }
});

function get_table_initilize() {
        var table = $('#userRoleTbl').dataTable({
            "processing": true,
            "serverSide": true,
            "destroy": true,
            "ajax": "/admin/list-user-role/",
            "searching": true,
            "ordering": true,
            "paging": true,
            "columnDefs": [
                {"targets": 1, "orderable": false},
                {"targets": 2, "orderable": false},
                {"targets": 3, "orderable": false},
                {"targets": 4, "orderable": false},
                {"targets": 5, "orderable": false},
            ]
        });
 }

function change_status(id){
    bootbox.confirm({
        title: "Roles",
        message: "<span class='center-block text-center'><b>Do you want to change status for this role ?<b></span>",
        buttons: {
            cancel: {
                label: '<i class="fa fa-times" style="color:red"></i> Cancel'
            },
            confirm: {
                label: '<i class="fa fa-check"></i> Yes'
            }
        },
        callback: function (result) {
             if (result == true) {
                $.ajax({
                    type: "GET",
                    url: '/admin/record-status-change/',
                    data: {
                        'role_id': id
                    },
                    success: function(response) {
                        console.log('response', response);
                        if (response.success == "true") {
                            bootbox.alert("<span class='center-block text-center'>Role status has changed !</span>");
                            get_table_initilize();
                        }else if (response.success == "user")
                                bootbox.alert("<span class='center-block text-center'>You Cannot In-Active role that contains Associated Users !</span>");
                    },
                    error: function(response) {
                        bootbox.alert("<span class='center-block text-center'>Role is not change !</span>");
                    },
                    beforeSend: function() {
                    $("#processing").show();
                    },
                    complete: function() {
                    $("#processing").hide();
                    }
                });
            }

        }
    });
}
function editRole(id) {
    $('label.error').hide();
    $('#editRoleModal').modal('show');
    $('.' + 'viewcheckbox').prop("checked", false);
    $('.' + 'viewcheckbox').closest('span').removeClass('checked');
    $.ajax({
        type: "GET",
        url: '/admin/view-edit-role/',
        data: {
            'role_id': id
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                $('#txt_roleId').val(response.userRole);
                $('#editRoleName').val(response.role);
                $('#editRoleDescription').val(response.description);
                $.each(response.privileges, function(index, value) {
                    $('.view' + value).prop("checked", true);
                    $('.view' + value).closest('span').addClass('checked');
                });
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

$(".root").change(function() {
    console.log(jQuery.fn.jquery);
    var className = $(this).attr('class').split(' ');
    if (this.checked) {
        $('.' + className[1]).prop("checked", true);
        $('.' + className[1]).closest('span').addClass('checked');
    } else {
        $('.' + className[1]).prop("checked", false);
        $('.' + className[1]).closest('span').removeClass('checked');
    }
});

$(".rootView").change(function() {
    console.log(jQuery.fn.jquery);
    var className = $(this).attr('class').split(' ');
    if (this.checked) {
        $('.' + className[1]).prop("checked", true);
        $('.' + className[1]).closest('span').addClass('checked');
    } else {
        $('.' + className[1]).prop("checked", false);
        $('.' + className[1]).closest('span').removeClass('checked');
    }
});

$("#selectAll").change(function() {
    console.log(jQuery.fn.jquery);
    var className = $(this).attr('class').split(' ');
    console.log($(this).attr('class'));
    console.log(className)
    if (this.checked) {
        $('.selectAll').prop("checked", true);
        $('.selectAll').closest('span').addClass('checked');
    } else {
        $('.selectAll').prop("checked", false);
        $('.selectAll').closest('span').removeClass('checked');
    }
});

$("#editSelectAll").change(function() {
    console.log(jQuery.fn.jquery);
    var className = $(this).attr('class').split(' ');
    console.log($(this).attr('class'));
    console.log(className)
    if (this.checked) {
        $('.selectAll').prop("checked", true);
        $('.selectAll').closest('span').addClass('checked');
    } else {
        $('.selectAll').prop("checked", false);
        $('.selectAll').closest('span').removeClass('checked');
    }
});

$("#editRoleBtn").click(function() {
var message = $('#editRoleName').val();
    if (message == "") {
      $("label#roleLabel").show();
      $("#editRoleName").focus();
      return false;
    } else {
        if ($('div.checkbox-group-view.required :checkbox:checked').length == 0) {
            $("label#privilegesLabel").show();
            return false;
        }
    }
    $.ajax({
        type: "POST",
        url: '/admin/update-user-role/',
        data: $('#editRoleFrm').serialize(),
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                bootbox.alert("<span class='center-block text-center'>Role has been edited successfully!</span>");
                $('#editRoleModal').modal('hide');
                get_table_initilize();
            }
        },
        error: function(response) {
            bootbox.alert("<span class='center-block text-center'>Role is not edit!</span>");
        },
        beforeSend: function() {
        },
        complete: function() {

        }
    });
});