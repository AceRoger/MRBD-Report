$(function(){
    $(".active-me").removeClass("active");
    $('#schedule_menu').addClass("active");

    $.validator.addMethod("valueNotEquals", function(value, element, arg){
        return arg != value;
    }, "Value must not equal arg.");

    $('#billCycleFrm').validate({
        debug: true,
        rules:{
            addCycleCode: "required",
            addCycleName: "required",
            city: {
                valueNotEquals: "0",
            },
            utility: {
                valueNotEquals: "0",
            },
            zone: {
                valueNotEquals: "0",
            },
            area: {
                valueNotEquals: "0",
            },
        },
        messages:{
            addCycleCode: "Please Enter bill cycle code",
            addCycleName: "Please Enter bill cycle name",
            city: "Please select city",
            utility: "Please select utility",
            zone: "Please select zone",
            area: "Please select area",
        }
    });
    $('#scheduleFrm').validate({
        rules:{
            billMonth: "required",
            billCycleCode: "required",
            startDate: {
                required: true,
            },
            endDate: {
                required: true,
            },
            accountingDate: {
                required: true,
            },
            estimatedDate: {
                required: true,
            }
        },
        messages:{
            billMonth: "Please select bill month",
            billCycleCode: "Please select bill cycle code",
            startDate: "Please enter valid start date",
            endDate: "Please enter valid end date",
            accountingDate: "Please enter valid accounting date",
            estimatedDate: "Please enter valid estimate date",
        }
    });
    $('#changeScheduleFrm').validate({
        rules:{
            dataStartDate: {
                required: true,
            },
            dataEstimatedDate: {
                required: true,
            },
            changeEndDate: {
                required: true,
            },
            changeAccountingDate: {
                required: true,
            }
        },
        messages:{
            dataStartDate: "Please enter valid start date",
            dataEstimatedDate: "Please enter valid estimate date",
            changeEndDate: "Please enter valid end date",
            changeAccountingDate: "Please enter valid accounting date",
        }
    });
    $('#coformedScheduleFrm').validate({
        rules:{
            dataStartDate: {
                required: true,
            },
            conformEndDate: {
                required: true,
            },
            dataEstimatedDate: {
                required: true,
            },
            conformAccountingDate: {
                required: true,
            }
        },
        messages:{
            dataStartDate: "Please enter valid start date",
            conformEndDate: "Please enter valid end date",
            dataEstimatedDate: "Please enter valid estimate date",
            conformAccountingDate: "Please enter valid accounting date",
        }
    });
    $('#rejectedScheduleFrm').validate({
        rules:{
            rejectedEnd: {
                required: true,
            },
            rejectedAccounting: {
                required: true,
            }
        },
        messages:{
            rejectedEnd: "Please enter valid end date",
            rejectedAccounting: "Please enter valid accounting date",
        }
    });
});

$("#searchTxt").keyup(function() {
    $(".col-md-3.testVal").each(function() {
        var count = ($(this).attr("id")).toLowerCase();
        if (count.indexOf(($("#searchTxt").val()).toLowerCase()) !== -1)
            $(this).show();
        else
            $(this).hide();
    });
});


$( document ).ready(function() {
    $("select#monthYear")[0].selectedIndex = 0;
    $("select#filterBy")[0].selectedIndex = 0;
});
function addNewBCC(){
    $('label.error').hide();
    $('#billCycleFrm').trigger("reset");
    $('#addNewCycleCode').modal('show');
    $('#createNewSchedule').modal('hide');
}
function createNewSchedule() {
    $('#scheduleFrm').trigger("reset");
    $('label.error').hide();
    $('#createNewSchedule').modal('show');
}

//TODO save bill cycle in database
$("#bcc_Submit_btn").click(function() {
$("#billCycleFrm input").each(function(index, value) {
        if (value.checkValidity() == false) {
            check_flag = false
            return false;
        } else {
            check_flag = true
        }
    });
    if (check_flag == false) {
        $("#add_bcc_btn").click();
        return false
    } else {
        $.ajax({
            type: "POST",
            url: '/schedule/add-bill-cycle/',
            data: $('#billCycleFrm').serialize(),
            success: function(response) {
                console.log('response', response);
                if (response.success == "true") {
                    $('#addNewCycleCode').modal('hide');
                    bootbox.alert("<span class='center-block text-center'>Bill Cycle has been created!</span>",function(){
                    location.reload();
                    });
                }else if (response.success == "Exist")
                    bootbox.alert("<span class='center-block text-center'>Bill cycle is already available in database !</span>");
                else
                    bootbox.alert("<span class='center-block text-center'>Server Connection failed !<br>Please try after some time.</span>");
            },
            error: function(response) {
                bootbox.alert("<span class='center-block text-center'>Data is not Stored !<br>Please enter valid data.</span>");
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

//TODO Bill Schedule Save Functionality Start
$("#submit_btn").click(function() {
    check_flag = true;

     var fit_start_time  = $("#startDate").val();
     var fit_end_time    = $("#endDate").val();
     var fit_acc_time  = $("#accountingDate").val();
     var fit_est_time    = $("#estimatedDate").val();

     fit_start_time=fit_start_time.split("/");
     fit_end_time=fit_end_time.split("/");
     fit_acc_time=fit_acc_time.split("/");
     fit_est_time=fit_est_time.split("/");

     st_dt=new Date(fit_start_time[2],fit_start_time[1]-1,fit_start_time[0])
     ed_dt=new Date(fit_end_time[2],fit_end_time[1]-1,fit_end_time[0])
     ac_dt=new Date(fit_acc_time[2],fit_acc_time[1]-1,fit_acc_time[0])
     et_dt=new Date(fit_est_time[2],fit_est_time[1]-1,fit_est_time[0])

        if( st_dt > ed_dt ){
            bootbox.alert("Please ensure that the <b>End Date</b> is greater than or equal to the Start Date.");
            check_flag = false
            return false;
        }
        if( st_dt > ac_dt ){
            bootbox.alert("Please ensure that the <b>Accounting Date</b> is greater than or equal to the Start Date.");
            check_flag = false
            return false;
        }
        if( st_dt > et_dt ){
            bootbox.alert("Please ensure that the <b>Estimated</b> Date is greater than or equal to the Start Date.");
            check_flag = false
            return false;
        }

    $("#scheduleFrm input,select").each(function(index, value) {


        if (value.checkValidity() == false) {
            check_flag = false
            return false;
        } else {
            check_flag = true
        }
    });
    if (check_flag == false) {
        $("#schedule_sbt_btn").click();
        return false
    } else {
        $.ajax({
            type: "POST",
            url: '/schedule/save-bill-schedule/',
            data: $('#scheduleFrm').serialize(),
            success: function(response) {
                console.log('response', response);
                if (response.success == "true") {
                    $('#createNewSchedule').modal('hide');
                    bootbox.alert("<span class='center-block text-center'>Schedule created successfully !</span>",function(){
                    refresh();
                    });
                }else if (response.success == "avail")
                    bootbox.alert("<span class='center-block text-center'>For this bill cycle schedule is already created in current month.</span>");
                 else if (response.success == "exist")
                    bootbox.alert("<span class='center-block text-center'>You cannot add new schedule for particular bill cycle until previous month reading is completed.</span>");
                else("#errorMessage")
            },
            error: function(response) {
                $('#createNewSchedule').modal('show');
                bootbox.alert("<span class='center-block text-center'>Data is not Stored !<br>Please enter valid data.</span>");
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
//Bill Schedule Save Functionality End

//Copy from Previous Button Functionality Start
function copyFromPrev() {
    bootbox.confirm({
        title: "Schedule",
        message: "<span class='center-block text-center'><b>Do you want to copy schedule from previous month ?<b></span>",
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
                    url: '/schedule/copy-from-previous/',
                     data:{
                        'monthYear':$("#monthYear").val()
                    },
                    success: function(response) {
                        console.log('response', response);
                        if (response.success == "Empty") {
                             bootbox.alert("<span class='center-block text-center'>Does not found any Completed Schedule to copy !</span>");
                        }if (response.success == "Open") {
                             bootbox.alert("<span class='center-block text-center'>Copy is not completed because of Schedule are open</span>");
                        }if (response.success == "true") {
                            bootbox.alert("<span class='center-block text-center'>Copy from previous is completed. Active bill schedule are not copied !</span>",
                            function(){ refresh(); });
                        } else("#errorMessage")
                    },
                    error: function(response) {
                        bootbox.alert("<span class='center-block text-center'>Schedule is not copy !</span>");
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


//TODO Change Bill Schedule Show edit modal Start
function changeSchedule(id) {
    $('#changeEndDate').val('');
    $('#changeAccountingDate').val('');
    $.ajax({
        type: "GET",
        url: '/schedule/change-schedule/',
        data: {
            'id': id
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                $('#changeBillMonth').text(response.month);
                $('#dataBillCycleCode').text(response.bill_cycle);
                $('#dataStartDate').val(response.start_date);
                $('#dataEstimatedDate').val(response.estimated_date);
                $('#changeEndDate').val(response.end_date);
                $('#changeAccountingDate').val(response.accounting_date);
                $('#changeSchedule_id').val(response.id);
                $('label.error').hide();
                $('#changeBillSchedule').modal('show');
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
//Change Bill Schedule Show edit modal End


//Change in Not Confirm Schedule Save Functionality Start
$("#changeSubmitButton").click(function() {
    check_flag = true;
     var fit_start_time  = $("#dataStartDate").val();
     var fit_end_time    = $("#changeEndDate").val();
     var fit_acc_time  = $("#changeAccountingDate").val();
     var fit_est_time    = $("#dataEstimatedDate").val();

     fit_start_time=fit_start_time.split("/");
     fit_end_time=fit_end_time.split("/");
     fit_acc_time=fit_acc_time.split("/");
     fit_est_time=fit_est_time.split("/");

     st_dt=new Date(fit_start_time[2],fit_start_time[1]-1,fit_start_time[0])
     ed_dt=new Date(fit_end_time[2],fit_end_time[1]-1,fit_end_time[0])
     ac_dt=new Date(fit_acc_time[2],fit_acc_time[1]-1,fit_acc_time[0])
     et_dt=new Date(fit_est_time[2],fit_est_time[1]-1,fit_est_time[0])

    if( st_dt > et_dt ){
            bootbox.alert("Please ensure that the <b>Estimated Date</b> is greater than or equal to the Start Date.");
            check_flag = false
            return false;
    }
    if( st_dt > ed_dt ){
            bootbox.alert("Please ensure that the <b>End Date</b> is greater than or equal to the Start Date.");
            check_flag = false
            return false;
    }
    if( st_dt > ac_dt ){
            bootbox.alert("Please ensure that the <b>Accounting Date</b> is greater than or equal to the Start Date.");
            check_flag = false
            return false;
    }

    $("#changeScheduleFrm input").each(function(index, value) {
        if (value.checkValidity() == false) {
            check_flag = false
            return false
        } else {
            check_flag = true
        }
    });

    if (check_flag == false) {
        $("#change_sbt_btn").click();
        return false
    } else {

        $.ajax({
            type: "POST",
            url: '/schedule/save-change-notConformed/',
            data: $('#changeScheduleFrm').serialize(),
            success: function(response) {
                console.log('response', response);
                if (response.success == "true") {
                   $('#changeBillSchedule').modal('hide');
                   bootbox.alert("<span class='center-block text-center'>Data has been saved & Status Changed Successfully !</span>",function(){
                    refresh();
                    });
                } else("#errorMessage")
            },
            error: function(response) {
                bootbox.alert("<span class='center-block text-center'>Data is not Stored !<br>Please enter valid data.</span>");
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
//Edit Bill Schedule Save Functionality End

//Change in Conform Schedule modal Start
function changeInConformTab(id) {
    $('#conformEndDate').val('');
    $('#conformAccountingDate').val('');

    $.ajax({
        type: "GET",
        url: '/schedule/change-conformed-tab/',
        data: {
            'id': id
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                $('#changeInConformMonth').text(response.month);
                $('#conformBillCycleCode').text(response.bill_cycle);
                $('#conformStartDate').text(response.start_date);
                $('#conformEstimatedDate').text(response.estimated_date);
                $('#conformEndDate,#hiddenEnd').val(response.end_date);
                $('#conformAccountingDate,#hiddenAccounting').val(response.accounting_date);
                $('#confirmSchedule_id').val(response.id);
                $('label.error').hide();
                $('#changeConformedSchedule').modal('show');
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

//Change in Conform Schedule Save Functionality Start
$("#conformSubmitButton").click(function() {
    check_flag = true;
     var fit_start_time  = $("#conformStartDate").val();
     var fit_end_time    = $("#conformEndDate").val();
     var fit_acc_time  = $("#conformAccountingDate").val();
     var end_date    = $("#hiddenEnd").val();
     var acc_time    = $("#hiddenAccounting").val();
     var fit_est_time    = $("#conformEstimatedDate").val();
     fit_start_time=fit_start_time.split("/");
     fit_end_time=fit_end_time.split("/");
     fit_acc_time=fit_acc_time.split("/");
     fit_est_time=fit_est_time.split("/");
     end_date=end_date.split("/");
     acc_time=acc_time.split("/");

     st_dt=new Date(fit_start_time[2],fit_start_time[1]-1,fit_start_time[0])
     ed_dt=new Date(fit_end_time[2],fit_end_time[1]-1,fit_end_time[0])
     ac_dt=new Date(fit_acc_time[2],fit_acc_time[1]-1,fit_acc_time[0])
     et_dt=new Date(fit_est_time[2],fit_est_time[1]-1,fit_est_time[0])
     end=new Date(end_date[2],end_date[1]-1,end_date[0])
     acc=new Date(acc_time[2],acc_time[1]-1,acc_time[0])

    if( end.toString() == ed_dt.toString() && acc.toString() == ac_dt.toString()){
            bootbox.alert("New <b>End Date</b> & <b>Accounting Date</b> is same as the old <b>End Date</b> & <b>Accounting Date</b>.<br> Please change one of them for continue");
            check_flag = false
            return false;
    }
    if( st_dt > et_dt ){
            bootbox.alert("Please ensure that the <b>Estimated Date</b> is greater than or equal to the Start Date.");
            check_flag = false
            return false;
    }
    if( st_dt > ed_dt ){
            bootbox.alert("Please ensure that the <b>End Date</b> is greater than or equal to the Start Date.");
            check_flag = false
            return false;
    }
    if( st_dt > ac_dt ){
            bootbox.alert("Please ensure that the <b>Accounting Date</b> is greater than or equal to the Start Date.");
            check_flag = false
            return false;
    }
    $("#coformedScheduleFrm input").each(function(index, value) {
        if (value.checkValidity() == false) {
            check_flag = false
            return false
        } else {
            check_flag = true
        }
    });

    if (check_flag == false) {
        $("#confirm_sbt_btn").click();
        return false
    } else {
        $.ajax({
            type: "POST",
            url: '/schedule/save-conformed-change/',
            data: $('#coformedScheduleFrm').serialize(),
            success: function(response) {
                console.log('response', response);
                if (response.success == "true") {
                    $('#changeConformedSchedule').modal('hide');
                    bootbox.alert("<span class='center-block text-center'>Data is Change & Mail is send to Approvar !</span>",function(){
                    refresh();
                    });
                } else("#errorMessage")
            },
            error: function(response) {
            $('#changeConformedSchedule').modal('show');
                bootbox.alert("<span class='center-block text-center'>Data is not Stored !<br>Please enter valid data.</span>");
            },
            beforeSend: function() {
            $('#changeConformedSchedule').modal('hide');
            $("#processing").show();
            },
            complete: function() {
            $("#processing").hide();
            }
        });
    }
});
//Edit Bill Schedule Save Functionality End

//showHistory in Conform Schedule modal Start
function showHistory(id) {
    $('#billCycleCode').val('');
    $('#startDate').val('');
    $('#endDate').val('');
    $('#accountingDate').val('');
    $('#estimatedDate').val('');
    $('#conformApprove').val('');
    $('#conformRemark').val('');
    $.ajax({
        type: "GET",
        url: '/schedule/show-history/',
        data: {
            'id': id
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                $('#historyBCC').text(response.schedule.bill_schedule);
                $('#historyStartDate').text(response.schedule.start_date);
                $('#historyEndDate').text(response.schedule.end_date);
                $('#historyAccountingDate').text(response.schedule.accounting_date);
                $('#historyEstimatedDate').text(response.schedule.estimated_date);
                $('#conformApprove').text(response.Approver);
                $('#conformRemark').text(response.remark);
                $('#historyId').val(response.id);
                $('#history').modal('show');
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

function sendMail(id) {
    $.ajax({
        type: "POST",
        url: '/schedule/send-mail/',
        data: {
            'id': id
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                bootbox.alert("<span class='center-block text-center'>Mail is send to Approvar !</span>",function(){
                    refresh();
                    });
            } else("#errorMessage")
        },
        error: function(response) {
            bootbox.alert("<span class='center-block text-center'>Mail is not send !</span>");
        },
        beforeSend: function() {},
        complete: function() {}
    });
}

function sendReminder(id) {
    $.ajax({
        type: "POST",
        url: '/schedule/send-Reminder-Mail/',
        data: {
            'id': id
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                bootbox.alert("<span class='center-block text-center'>Reminder Mail is send to Approvar!</span>");
            } else("#errorMessage")
        },
        error: function(response) {
            bootbox.alert("<span class='center-block text-center'>Mail is not send !</span>");
        },
        beforeSend: function() {
        $("#processing").show();
        },
        complete: function() {
        $("#processing").hide();
        }
    });
}

//Change in  Schedule modal Start
function changeInRejectedTab(id) {
    $('#rejectedEnd').val('');
    $('#rejectedAccounting').val('');
    $('label.error').hide();
    $('#changeRejectedSchedule').modal('show');
    $.ajax({
        type: "GET",
        url: '/schedule/change-rejected-schedule/',
        data: {
            'id': id
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                $('#rejectedMonth').text(response.month);
                $('#rejectedCode').text(response.bill_cycle);
                $('#rejectedStart').text(response.start_date);
                $('#rejectedEstimate').text(response.estimated_date);
                $('#rejectedEnd,#hideRejectEnd').val(response.end_date);
                $('#rejectedAccounting,#hideRejectAcc').val(response.accounting_date);
                $('#rejectedSchedule_id').val(response.id);
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


//Save Functionality in Rejected Schedule Start
$("#rejectedApprovalbutton").click(function() {
    check_flag = true;

     var fit_start_time  = $("#rejectedStart").text();
     var fit_end_time    = $("#rejectedEnd").val();
     var fit_acc_time  = $("#rejectedAccounting").val();
     var end_date    = $("#hideRejectEnd").val();
     var acc_time    = $("#hideRejectAcc").val();


     fit_start_time=fit_start_time.split("/");
     fit_end_time=fit_end_time.split("/");
     fit_acc_time=fit_acc_time.split("/");
     end_date=end_date.split("/");
     acc_time=acc_time.split("/");

     st_dt=new Date(fit_start_time[2],fit_start_time[1]-1,fit_start_time[0])
     ed_dt=new Date(fit_end_time[2],fit_end_time[1]-1,fit_end_time[0])
     ac_dt=new Date(fit_acc_time[2],fit_acc_time[1]-1,fit_acc_time[0])
     end=new Date(end_date[2],end_date[1]-1,end_date[0])
     acc=new Date(acc_time[2],acc_time[1]-1,acc_time[0])

    if( end.toString() == ed_dt.toString() && acc.toString() == ac_dt.toString()){
            bootbox.alert("New <b>End Date</b> & <b>Accounting Date</b> is same as the old <b>End Date</b> & <b>Accounting Date</b>. Please change one of them for continue");
            check_flag = false
            return false;
    }

    if( st_dt > ed_dt ){
            bootbox.alert("Please ensure that the <b>End Date</b> is greater than or equal to the Start Date.");
            check_flag = false
            return false;
    }
    if( st_dt > ac_dt ){
            bootbox.alert("Please ensure that the <b>Accounting Date</b> is greater than or equal to the Start Date.");
            check_flag = false
            return false;
    }

    $("#rejectedScheduleFrm input").each(function(index, value) {
        if (value.checkValidity() == false) {
            check_flag = false
            return false
        } else {
            check_flag = true
        }
    });

    if (check_flag == false) {
        $("#rejected_sbt_btn").click();
        return false
    } else {
        $.ajax({
            type: "POST",
            url: '/schedule/save-rejected-change/',
            data: $('#rejectedScheduleFrm').serialize(),
            success: function(response) {
                console.log('response', response);
                if (response.success == "true") {
                    $('#changeRejectedSchedule').modal('hide');
                    bootbox.alert("<span class='center-block text-center'>Data is Change & Mail is send to Approvar !</span>",function(){
                    refresh();
                    });
                } else("#errorMessage")
            },
            error: function(response) {
            $('#changeRejectedSchedule').modal('show');
                bootbox.alert("<span class='center-block text-center'>Data is not Stored !<br>Please enter valid data.</span>");
            },
            beforeSend: function() {
            $('#changeRejectedSchedule').modal('hide');
            $("#processing").show();
            },
            complete: function() {
             $("#processing").hide();
            }
        });
    }
});
//Edit Bill Schedule Save Functionality End

function pendingHistory(pendingHistoryId) {
    $('#pendingHistory').modal('show');
    $.ajax({
        type: "GET",
        url: '/schedule/pending-history/',
        data: {
            'id': pendingHistoryId
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                $('#pendingBCC').text(response.get_original.bill_cycle);
                $('#pendingStartDate').text(response.get_original.start_date);
                $('#pendingEndDate').text(response.get_original.end_date);
                $('#pendingEstimatedDate').text(response.get_original.estimated_date);
                $('#pendingAccountingDate').text(response.get_original.accounting_date);
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

function rejectedHistoryBtn(rejectedHistoryId) {
    $('#rejectedHistory').modal('show');
    $.ajax({
        type: "GET",
        url: '/schedule/rejected-history/',
        data: {
            'id': rejectedHistoryId
        },
        success: function(response) {
            console.log('response', response);
            if (response.success == "true") {
                $('#rejectedBillMonth').text(response.details.month);
                $('#rejectedBCC').text(response.details.bill_cycle);
                $('#rejectedStartDate').text(response.details.start_date);
                $('#rejectedEndDate').text(response.details.end_date);
                $('#rejectedExEndDate').text(response.changes_list.extended_end_date);
                $('#rejectedAccountingDate').text(response.details.accounting_date);
                $('#rejectedEstimatedDate').text(response.details.estimated_date);
                $('#rejectedExAccountingDate').text(response.changes_list.extended_accounting_date);
                $('#approver').text(response.billDetails.Approver);
                $('#remark').text(response.billDetails.remark);
            }
        },
        error: function(response) {
            console.log(response)

        },
        beforeSend: function() {
        },
        complete: function() {
        }
    });
}

function refresh(){
yearMonth = $("#monthYear").val()
    console.log(yearMonth)
    $.ajax({
        type: "GET",
        url: "/schedule/get-bill-schedules/",
        data: {
            'yearMonth': yearMonth
        },
        success: function(response) {
            console.log('response', response)
            $('#scheduleBody').html('');
            $("#filterBy").val('All');
            $('#scheduleBody').html(response);

            $('#lbl_totalCopied').text($('#totalCopied').val()+ ' Total');
            $('#lbl_totalNotConfirmed').text($('#totalNotConfirmed').val());
            $('#lbl_totalConfirmed').text($('#totalConfirmed').val());
            $('#lbl_totalPendding').text($('#totalPendding').val());
            $('#lbl_totalRejected').text($('#totalRejected').val());

        },
        error: function(response) {
            console.log('response', response);
        },
        beforeSend: function() {
        $("#processing").show();
        },
        complete: function() {
        $("#processing").hide();
        }
    });
}

$("#monthYear").change(function() {
    refresh();
});

$("#filterBy").change(function() {
    yearMonth = $("#monthYear").val()
    filterBy = $("#filterBy").val()
    console.log(yearMonth)
    $.ajax({
        type: "GET",
        url: "/schedule/get-bill-schedules-byfilter/",
        data: {
            'yearMonth': yearMonth,
            'filterBy': filterBy
        },
        success: function(response) {
            console.log('response', response)
            $('#scheduleBody').html('');
            $('#scheduleBody').html(response);
        },
        error: function(response) {
            console.log('response', response);
        },
        beforeSend: function() {
        $("#processing").show();
        },
        complete: function() {
        $("#processing").hide();
        }
    });
});