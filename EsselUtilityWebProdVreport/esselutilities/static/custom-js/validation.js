$(document).ready(function(){

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

        $('#accountingDate').datepicker({
            format: 'dd/mm/yyyy',
            minDate: 1,
            startDate: 'd',
            autoclose: true
        });

        $('#estimatedDate').datepicker({
            format: 'dd/mm/yyyy',
            minDate: 1,
            startDate: 'd',
            autoclose: true
        });

        $('#dataStartDate').datepicker({
            format: 'dd/mm/yyyy',
            minDate: 1,
            startDate: 'd',
            autoclose: true
        });

        $('#dataEstimatedDate').datepicker({
            format: 'dd/mm/yyyy',
            minDate: 1,
            startDate: 'd',
            autoclose: true
        });

        $('#changeAccountingDate').datepicker({
            format: 'dd/mm/yyyy',
            minDate: 1,
            startDate: 'd',
            autoclose: true
        });

        $('#changeEndDate').datepicker({
            format: 'dd/mm/yyyy',
            minDate: 1,
            startDate: 'd',
            autoclose: true
        });

        $('#conformEndDate').datepicker({
            format: 'dd/mm/yyyy',
            minDate: 1,
            startDate: 'd',
            autoclose: true
        });

        $('#conformAccountingDate').datepicker({
            format: 'dd/mm/yyyy',
            minDate: 1,
            startDate: 'd',
            autoclose: true
        });

        $('.newdatepickerDate').datepicker({
            format: "dd/mm/yyyy",
            autoclose: false,
            changeMonth: true,
            changeYear: true,
            yearRange: "-100:+0",
        });

var page_number;
monthChanged(page_number);

});

var page_number;


function currentPage(page_number){
monthChanged(page_number);
}

function call_prev(page_number){
monthChanged(page_number);
}


function call_next(page_number){
    monthChanged(page_number);
}

$("#monthYear").change(function(){
    monthChanged(page_number);
//    url = "/validate/validate-jobcard-list/"+ monthYear;
//    window.location.href = url;
});


function monthChanged(page_number){
 monthYear=$("#monthYear").val();
                $.ajax({
                    type: "GET",
                    url:  "/validate/validate-jobcard-list/",
                    data:{
                    'month' : monthYear,
                    'page_number':page_number,
                    },
                    success: function(response) {
                            //alert('Consumer validated successfully!');
                                console.log(response);
                            $("#validationBody").html('');
                            $("#validationBody").html(response);
                    },
                    error: function(response) {
                        bootbox.alert('An unexpected error occured!');
                    },
                    beforeSend: function() {
                    $("#processing").show();
                    },
                    complete: function() {
                    $("#processing").hide();
                    }
                });
            }





function isNumberKey(evt, element)
{
  var charCode = (evt.which) ? evt.which : evt.keyCode;
  if (  (charCode != 46 && charCode > 31 && (charCode < 48 || charCode > 57)) ||  charCode == 46 )
     return false;

 // if ($(element).val().indexOf('.') == 1) {
 //      return false;
 //    }
  return true;
}

$("#searchTxt").keyup(function(){
    $(".testVal").each(function(){
        var count = $(this).attr("id");
        if(count.indexOf($("#searchTxt").val()) !== -1)
            $(this).show();
        else
            $(this).hide();
    });
});


function submitValidation(){
    // var r = confirm("Are you sure you want to confirm this validate?");
    // if (r == true) {
    //     $("#validate1form").submit();
    // }else {
    //     return false;
    // }

    bootbox.confirm({
        title: "Validation",
        message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Are you sure you want to confirm this validate?<b>",
        buttons: {
            cancel: {
                label: '<i class="fa fa-times" style="color:red"></i> Cancel'
            },
            confirm: {
                label: '<i class="fa fa-check"></i> Confirm'
            }
        },
        callback: function (result) {
             if (result == true) {
                $("#validate1form").submit();
            }
        }
    });
}

function submitValidation1(url){
    bootbox.confirm({
        title: "Validation",
        message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Are you sure you want to confirm this validate complete?<b>",
        buttons: {
            cancel: {
                label: '<i class="fa fa-times" style="color:red"></i> Cancel'
            },
            confirm: {
                label: '<i class="fa fa-check"></i> Confirm'
            }
        },
        callback: function (result) {
             if (result == true) {
                $('#validate1form').attr('action', url);
                $("#validate1form").submit();
            }
        }
    });
}

function submitRevisit(url){
    bootbox.confirm({
        title: "Validation",
        message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Are you sure you want to send this record to revisit?<b>",
        buttons: {
            cancel: {
                label: '<i class="fa fa-times" style="color:red"></i> Cancel'
            },
            confirm: {
                label: '<i class="fa fa-check"></i> Confirm'
            }
        },
        callback: function (result) {
             if (result == true) {
                $('#validate1form').attr('action', url);
                $("#validate1form").submit();
            }

        }
    });
}

function validate_level_one_two(url) {
    bootbox.confirm({
        title: "Validation",
        message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Are you sure you want to confirm this validate?<b>",
        buttons: {
            cancel: {
                label: '<i class="fa fa-times" style="color:red"></i> Cancel'
            },
            confirm: {
                label: '<i class="fa fa-check"></i> Confirm'
            }
        },
        callback: function (result) {
             if (result == true) {
                $.ajax({
                    type: "POST",
                    url: url,
                    data: $('#validate1form').serialize(),
                    success: function(response) {
                        if (response.success == "true") {
                            //alert('Consumer validated successfully!');
                            bootbox.alert('Consumer validated successfully!');
                            $("#validationstatus").html('');
                            $("#validationstatus").html('<b>Validation completed</b>');
                            $("#buttonsDiv").hide();
                        }else{
                            // alert('An unexpected error occured!');
                            bootbox.alert('An unexpected error occured!');
                        }
                    },
                    error: function(response) {
                        bootbox.alert('An unexpected error occured!');
                    },
                    beforeSend: function() {
                    },
                    complete: function() {
                    }
                });
            }

        }
    });
}

function searchConsumer(url){
    $.ajax({
        type: "POST",
        url: url,
        data: $('#consumerSearchform').serialize(),
        success: function(response) {
            if (response.success == "true") {

                if (response.validator == 1){
                    window.location.href = "/validate/validation-level-one/" + response.billcycleid + "/" +  response.month + "/" +  response.validatorAssigned + "/";
                }else{
                    window.location.href = "/validate/validation-level-two/" + response.billcycleid + "/" +  response.month + "/" +  response.validatorAssigned + "/";
                }
            }else{
                bootbox.alert('Consumer not fiound OR not assigned to you for validation!');
            }
        },
        error: function(response) {
            bootbox.alert('An unexpected error occured!');
        },
        beforeSend: function() {
        },
        complete: function() {
        }
    });
}

function changeConsumptionV1(){
    var a;
    a = $('#current_meter_reading_v1').val() - $('#prevreading').val()
    $('#consumptionv1').html('');
    $('#consumptionv1').html(a);
}

function changeConsumptionV2(){
    var a;
    a = $('#current_meter_reading_v2').val() - $('#prevreading').val()
    $('#consumptionv2').html('');
    $('#consumptionv2').html(a);
}

function submitVerify(url){

    $.ajax({
            type: "POST",
            url: url,
            data: $('#verifyform').serialize(),
            success: function(response) {
                if (response.success == "true") {
                    bootbox.alert('Consumer already exist!');
                    // alert("Consumer already exist!");
                }else{
                    bootbox.alert('Consumer already exist!');
                }
            },
            error: function(response) {
                bootbox.alert('An unexpected error occured!');
                // alert('An unexpected error occured!');
            },
            beforeSend: function() {
            },
            complete: function() {
            }
        });

}

function discardConsumer(url, url1){
    bootbox.confirm({
        title: "Validation",
        message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Are you sure you want discard this Consumer?<b>",
        buttons: {
            cancel: {
                label: '<i class="fa fa-times" style="color:red"></i> Cancel'
            },
            confirm: {
                label: '<i class="fa fa-check"></i> Confirm'
            }
        },
        callback: function (result) {
             if (result == true) {
                $.ajax({
                    type: "POST",
                    url: url,
                    data: $('#verifyform').serialize(),
                    success: function(response) {
                        if (response.success == "true") {
                            bootbox.alert("Consumer Descarded!");
                            window.location.href = url1;
                        }else{
                            bootbox.alert('Consumer does not exist!');
                            window.location.href = url1;
                        }
                    },
                    error: function(response) {
                        bootbox.alert('An unexpected error occured!');
                    },
                    beforeSend: function() {
                    },
                    complete: function() {
                    }
                });
            }
        }
    });
}



function addConsumer(url, url1){
    bootbox.confirm({
        title: "Validation",
        message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Are you sure you want add this Reading?<b>",
        buttons: {
            cancel: {
                label: '<i class="fa fa-times" style="color:red"></i> Cancel'
            },
            confirm: {
                label: '<i class="fa fa-check"></i> Confirm'
            }
        },
        callback: function (result) {
             if (result == true) {
                $.ajax({
                    type: "POST",
                    url: url,
                    data: $('#verifyform').serialize(),
                    success: function(response) {
                        if (response.success == "true") {
                            window.location.href = url1;
                        }else{
                            bootbox.alert('Consumer does not exist! Reading cannot be added. Please regularise the consumer');
                            window.location.href = url1;
                        }
                    },
                    error: function(response) {
                        bootbox.alert('An unexpected error occured!');
                    },
                    beforeSend: function() {
                    },
                    complete: function() {
                    }
                });
            }
        }
    });
}





function submitAddDuplicate(url,url1){
    bootbox.confirm({
        title: "Validation",
        message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Are you sure you want to confirm this Reading?<b>",
        buttons: {
            cancel: {
                label: '<i class="fa fa-times" style="color:red"></i> Cancel'
            },
            confirm: {
                label: '<i class="fa fa-check"></i> Confirm'
            }
        },
        callback: function (result) {
             if (result == true) {
                $.ajax({
                    type: "POST",
                    url: url,
                    data: $('#duplicateForm').serialize(),
                    success: function(response) {
                        if (response.success == "true") {
                            bootbox.alert("Reading Added successfully!");
                        }else{
                            bootbox.alert('Cant add reading!');
                        }
                        if(url1 == "")
                            window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;
                        else
                            window.location.href = url1
                    },
                    error: function(response) {
                        bootbox.alert('An unexpected error occured!');
                    },
                    beforeSend: function() {
                    },
                    complete: function() {
                    }
                });
            }
        }
    });

}


function check_duplicate_record01(url,url1){
    $.ajax({
            type: "POST",
            url: '/validate/check-duplicate-existence/',
            data: $('#duplicateForm').serialize(),
            success: function(response) {
                if (response.success == "true") {

                    if (response.result == "exist") {
                            bootbox.confirm({
                                title: "Validation",
                                message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Reading is already present for this consumer, do you still want to add or abort?<b>",
                                buttons: {
                                    cancel: {
                                        label: '<i class="fa fa-times" style="color:red"></i> Abord'
                                    },
                                    confirm: {
                                        label: '<i class="fa fa-check"></i> Add'
                                    }
                                },
                                callback: function (result) {
                                    if (result == true) {
                                        $.ajax({
                                                type: "POST",
                                                url: url,
                                                data: $('#duplicateForm').serialize(),
                                                success: function(response) {
                                                    if (response.success == "true") {
                                                        bootbox.alert("Reading Added successfully!");
                                                    }else{
                                                        bootbox.alert('Cant add reading!');
                                                    }
                                                    if(url1 == "")
                                                        window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;
                                                    else
                                                        window.location.href = url1
                                                },
                                                error: function(response) {
                                                    bootbox.alert('An unexpected error occured!');
                                                },
                                                beforeSend: function() {
                                                },
                                                complete: function() {
                                                }
                                            });
                                        }

                                    else {
                                        $.ajax({
                                            type: "POST",
                                            url: '/validate/rejectduplicate/',
                                            data: $('#duplicateForm').serialize(),
                                            success: function(response) {
                                                if (response.success == "true") {
                                                    bootbox.alert("Reading Rejected successfully.");
                                                }else{
                                                    bootbox.alert('An unexpected error occured!');
                                                }
                                                if(url1 == "")
                                                    window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;
                                                else
                                                    window.location.href = url1
                                            },
                                            error: function(response) {
                                                bootbox.alert('An unexpected error occured!');
                                            },
                                            beforeSend: function() {
                                            },
                                            complete: function() {
                                            }
                                        });

                                     }
                                  }
                             });

                    }
                    else if (response.result == "notexist") {
                        submitAddDuplicate(url,url1)
                    }

                }else{
                    bootbox.alert('server error !');
                }
            },
            error: function(response) {
                bootbox.alert('An unexpected error occured!');
            },
            beforeSend: function() {
            },
            complete: function() {
            }
    });
}



function check_duplicate_record(url,url1){
    $.ajax({
            type: "POST",
            url: '/validate/check-duplicate-existence/',
            data: $('#duplicateForm').serialize(),
            success: function(response) {
                if (response.success == "true") {

                    if (response.result == "exist") {

                             var buttons = {
                                        btn1: {
                                          label: '<i class="fa fa-times" style="color:red"></i> Cancel',
                                           "class" : "primary",
                                          callback: function() {

                                          }
                                        },
                                        btn2: {
                                          label: '<i class="fa fa-times" style="color:blue"></i> Abort',
                                           "class" : "primary",
                                          callback: function() {
                                                 $.ajax({
                                                    type: "POST",
                                                    url: '/validate/rejectduplicate/',
                                                    data: $('#duplicateForm').serialize(),
                                                    success: function(response) {
                                                        if (response.success == "true") {
                                                            bootbox.alert("Reading Rejected successfully.");
                                                        }else{
                                                            bootbox.alert('An unexpected error occured!');
                                                        }
                                                        if(url1 == "")
                                                            window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;
                                                        else
                                                            window.location.href = url1
                                                    },
                                                    error: function(response) {
                                                        bootbox.alert('An unexpected error occured!');
                                                    },
                                                    beforeSend: function() {
                                                    },
                                                    complete: function() {
                                                    }
                                                });
                                            }
                                        },
                                        btn3: {
                                          label: '<i class="fa fa-times" style="color:green"></i> Add',
                                          callback: function() {
                                              $.ajax({
                                                type: "POST",
                                                url: url,
                                                data: $('#duplicateForm').serialize(),
                                                success: function(response) {
                                                    if (response.success == "true") {
                                                        bootbox.alert("Reading Added successfully!");
                                                    }else{
                                                        bootbox.alert('Cant add reading!');
                                                    }
                                                    if(url1 == "")
                                                        window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;
                                                    else
                                                        window.location.href = url1
                                                },
                                                error: function(response) {
                                                    bootbox.alert('An unexpected error occured!');
                                                },
                                                beforeSend: function() {
                                                },
                                                complete: function() {
                                                }
                                            });

                                          }
                                        },
                                      }

                                      bootbox.dialog({
                                        title: "title",
                                        message: "<span class='center-block text-center'><b>Reading is already present for this consumer, do you still want to add or abort?<b></span>",
                                        buttons: buttons
                                      });


                    }
                    else if (response.result == "notexist") {
                        submitAddDuplicate(url,url1)
                    }

                }else{
                    bootbox.alert('server error !');
                }
            },
            error: function(response) {
                bootbox.alert('An unexpected error occured!');
            },
            beforeSend: function() {
            },
            complete: function() {
            }
    });
}









function submitRejectDuplicate(url,url1){
    bootbox.confirm({
        title: "Validation",
        message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Are you sure you want to reject this Reading?<b>",
        buttons: {
            cancel: {
                label: '<i class="fa fa-times" style="color:red"></i> Cancel'
            },
            confirm: {
                label: '<i class="fa fa-check"></i> Confirm'
            }
        },
        callback: function (result) {
             if (result == true) {
                $.ajax({
                    type: "POST",
                    url: url,
                    data: $('#duplicateForm').serialize(),
                    success: function(response) {
                        if (response.success == "true") {
                            bootbox.alert("Reading Rejected successfully.");
                        }else{
                            bootbox.alert('An unexpected error occured!');
                        }
                        if(url1 == "")
                            window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;
                        else
                            window.location.href = url1
                    },
                    error: function(response) {
                        bootbox.alert('An unexpected error occured!');
                    },
                    beforeSend: function() {
                    },
                    complete: function() {
                    }
                });
            }
        }
    });
}

function submitViewDuplicate(url){
    window.location.href = url;
}

$("#billcycle_change").change(function() {
    window.location.href = '/validate/validator-summery/'+ $("#monthYear_change").val() +"/"+ $("#billcycle_change").val()+"/"+ $("#role_change").val();
});

$("#role_change").change(function() {
    window.location.href = '/validate/validator-summery/'+ $("#monthYear_change").val() +"/"+ $("#billcycle_change").val()+"/"+ $("#role_change").val();
});
$("#monthYear_change").change(function() {
    window.location.href = '/validate/validator-summery/'+ $("#monthYear_change").val() +"/"+ $("#billcycle_change").val()+"/"+ $("#role_change").val();
});
/*  Added by Imran */

$(document).ready(function(){
    if($("#messageid").val() == 1){
        toastr.info($("#messagename").val());
    }

    $(function(){
        $(".active-me").removeClass("active");
        $('#validate_menu').addClass("active");
    });

    $("img.zoom").mouseover(function() {
        $(".mydiv").show();
    });
    $("img.zoom").mouseout(function() {
        $(".mydiv").hide();
    });

    $("img.zoom1").mouseover(function() {
        $(".mydiv1").show();
    });
    $("img.zoom1").mouseout(function() {
        $(".mydiv1").hide();
    });
    $("img.zoom2").mouseover(function() {
        $(".mydiv2").show();
    });
    $("img.zoom2").mouseout(function() {
        $(".mydiv2").hide();
    });
    $("img.zoom3").mouseover(function() {
        $(".mydiv3").show();
    });
    $("img.zoom3").mouseout(function() {
        $(".mydiv3").hide();
    });
    $("img.zoom4").mouseover(function() {
        $(".mydiv4").show();
    });
    $("img.zoom4").mouseout(function() {
        $(".mydiv4").hide();
    });

    $("img.zoom5").mouseover(function() {
        $(".mydiv5").show();
    });
    $("img.zoom5").mouseout(function() {
        $(".mydiv5").hide();
    });
    $("img.zoom6").mouseover(function() {
        $(".mydiv6").show();
    });
    $("img.zoom6").mouseout(function() {
        $(".mydiv6").hide();
    });

    $("img.zoom7").mouseover(function() {
        $(".mydiv7").show();
    });
    $("img.zoom7").mouseout(function() {
        $(".mydiv7").hide();
    });


    var table = $('#table-consumer-list').dataTable({
            "processing": true,
            "searching": true,
            "ordering": true,
            "paging": true,
            "columnDefs": [
                {"targets": 3, "orderable": false},
                {"targets": 4, "orderable": false},
                {"targets": 5, "orderable": false},
                {"targets": 7, "orderable": false},
            ]
        });

    var table = $('#table-consumer-list1').dataTable({
            "processing": true,
            "searching": true,
            "ordering": true,
            "paging": true,
            "columnDefs": [
                {"targets": 3, "orderable": false},
                {"targets": 4, "orderable": false},
                {"targets": 5, "orderable": false},
            ]
        });
});

function processImage($image,pWidth,pHeight){

    console.log("In process image!");

    var maxWidth = parseInt(pWidth); // Max width for the $image
    var maxHeight = parseInt(pHeight);    // Max height for the $image
    var ratio = 0;  // Used for aspect ratio
    var width = $image.width();    // Current $image width
    var height = $image.height();  // Current $image height

    console.log("width : "+width);
    console.log("height : "+height);

    if (($image.attr('src')!=="") && (width == 0))
    {
        setTimeout(function(){
            processImage($image,pWidth,pHeight);
        },1000);
        return;
    }
    // Check if the current width is larger than the max
    if(width > maxWidth){
        ratio = maxWidth / width;   // get ratio for scaling $image
        $image.css("width", maxWidth); // Set new width
        $image.css("height", height * ratio);  // Scale height based on ratio
        height = height * ratio;    // Reset height to match scaled $image
        width = width * ratio;    // Reset width to match scaled $image
    }

    // Check if current height is larger than max
    if(height > maxHeight){
        ratio = maxHeight / height; // get ratio for scaling $image
        $image.css("height", maxHeight);   // Set new height
        $image.css("width", width * ratio);    // Scale width based on ratio
        width = width * ratio;    // Reset width to match scaled $image
        height = height * ratio;    // Reset height to match scaled $image
    }
    $image.show();
}
