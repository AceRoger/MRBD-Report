$( document ).ready(function() {
    get_table_initilize();
});
function get_table_initilize() {
        var table = $('#approvalTable').dataTable({
            "processing": true,
            "serverSide": true,
            "destroy": true,
            "ajax": "/schedule/approval-list/",
            "searching": true,
            "ordering": true,
            "paging": true,
            "columnDefs": [
                {"targets": 1, "orderable": false},
                {"targets": 2, "orderable": false},
                {"targets": 3, "orderable": false},
                {"targets": 4, "orderable": false},
            ]
        });
 }
//TODO show list of pending record
function approval(id){
$('label.error').hide();
$("#remark").val('');
$.ajax({
        type: "GET",
        url: '/schedule/approval-Info/',
        data: {
            'id': id
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                $('#pendingBCC').text(response.get_original.bill_cycle);
                $('#pendingStartDate').text(response.get_original.start_date);
                $('#pendingEndDate').text(response.get_original.end_date);
                $('#pendingEstimatedDate').text(response.get_original.estimated_date);
                $('#pendingAccountingDate').text(response.get_original.accounting_date);
                $('#approval_id').val(response.get_original.id);
                $("#approveChangeModal").modal('show');
                $('#change').html('');
                $(response.changes_list).each(function(index, element) {

                    srNo = index + 1;
                    if (element.status == "Confirmed") {
                        $('#change').append('<div class="row"><div class="col-md-3 form-group"><label style="font-size: 16px !important;"> Change ' + srNo + '</label> </div>' + '<div class="col-md-6 form-group"><span class="class="font-green-jungle"" name="pendingEstimatedDate" id="pstimatedDate" style="font-size: 16px !important;">' + element.status + '</span></div></div>' + '<div class="row "><div class="form-group col-md-3"><label class="font-grey-mint">Accounting Date</label><br> <span>' + element.change_accounting_date + '</span></div>' + '<div class="col-md-3 form-group"><label class="font-grey-mint">End Date </label><br><span>' + element.change_end_date + '</span></div> </div>');
                    } else if (element.status == "Pending Approval") {
                        $('#change').append('<div class="row"><div class="col-md-3 form-group"><lable style="font-size: 16px !important;"> Change ' + srNo + '</label> </div>' + '<div class="col-md-6 form-group"><span class="font-yellow-casablanca" name="pendingEstimatedDate" id="pstimatedDate" style="font-size: 16px !important;">' + element.status + '</span></div></div>' + '<div class="row "><div class="form-group col-md-3"><label class="font-grey-mint">Accounting Date</label><br> <span>' + element.change_accounting_date + '</span></div>' + '<div class="col-md-3 form-group"><label class="font-grey-mint">End Date </label><br><span>' + element.change_end_date + '</span></div> </div>');
                    } else if (element.status == "Rejected") {
                        $('#change').append('<div class="row"><div class="col-md-3 form-group"><label style="font-size: 16px !important;"> Change ' + srNo + '</label> </div>' + '<div class="col-md-6 form-group"><span class="font-red-flamingo" name="pendingEstimatedDate" id="pstimatedDate" style="font-size: 16px !important;">' + element.status + '</span></div></div>' + '<div class="row "><div class="form-group col-md-3"><label class="font-grey-mint">Accounting Date</label><br> <span>' + element.change_accounting_date + '</span></div>' + '<div class="col-md-3 form-group"><label class="font-grey-mint">End Date </label><br><span>' + element.change_end_date + '</span></div> </div>');
                    } else("#errorMessage")

                    console.log(element);
                });
            }
        },
        error: function(response) {
            console.log(response)

        },
        beforeSend: function() {
        $("#processing").show();
        },
        complete: function() {
        $("#processing").hide();
        }
    });
}
//TODO Approve Schedule changes
$("#appoveChanges").click(function() {
var message = $("textarea#remark").val();
    if (message == "") {
      $("label#remarkLabel").show();
      $("textarea#remark").focus();
      return false;
    }else {
        bootbox.confirm({
        title: "Schedule",
        message: "<span class='center-block text-center'><b>Do you want to Approve schedule changes ?<b></span>",
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
                    type: "POST",
                    url: '/schedule/approve-changes/',
                    data: $('#approvalFrm').serialize(),
                    success: function(response) {
                        console.log('response', response);
                        if (response.success == "true") {
                            $("#approveChangeModal").modal('hide');
                            bootbox.alert("<span class='center-block text-center'>Schedule is successfully Approved!</span>",function(){
                            location.reload();
                            });
                        } else("#errorMessage")
                    },
                    error: function(response) {
                        bootbox.alert('Schedule is not approve.');
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
});

//TODO Reject Schedule changes
$("#rejectChanges").click(function() {
var message = $("textarea#remark").val();
    if (message == "") {
      $("label#remarkLabel").show();
      $("textarea#remark").focus();
      return false;
    }else {
        bootbox.confirm({
        title: "Schedule",
        message: "<span class='center-block text-center'><b>Do you want to Reject schedule changes ?<b></span>",
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
                    type: "POST",
                    url: '/schedule/reject-changes/',
                    data: $('#approvalFrm').serialize(),
                    success: function(response) {
                        console.log('response', response);
                        if (response.success == "true") {
                            $("#approveChangeModal").modal('hide');
                            bootbox.alert("<span class='center-block text-center'>Schedule is Reject and send for change!</span>",function(){
                            location.reload();
                            });
                        } else("#errorMessage")
                    },
                    error: function(response) {
                        bootbox.alert('Schedule is not reject.');
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
});
