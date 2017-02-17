$(function() {
    $(".active-me").removeClass("active");
    $('#upload_menu').addClass("active");

    $("#monthYear option:eq(0)").prop("selected", true)
    $("#filterBy option:eq(0)").prop("selected", true)

    $("#searchTxt").keyup(function(){
        $(".col-md-3.testVal").each(function(){
            var count = $(this).attr("id");
            if(count.indexOf($("#searchTxt").val()) !== -1)
                $(this).show();
            else
                $(this).hide();
        });
    });
});

function refresh_upload(){
yearMonth=$("#monthYear").val()
    console.log(yearMonth)
     $.ajax({
        type: "GET",
        url: "/upload/get-bill-cycles/",
        data: {'yearMonth':yearMonth},
        success: function(response) {
                console.log('response',response)
                $('#importbody').html('');
                $("#filterBy").val('All');
                $('#importbody').html(response);

                $("#lbl_totalRecord").text($('#totalRecord').val()+' Total')
                $("#lbl_totalUploaded").text($('#totalUploaded').val())
                $("#lbl_totalPending").text($('#totalPending').val())
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


$("#monthYear").change(function(){
    refresh_upload()
});

$("#filterBy").change(function(){
    yearMonth=$("#monthYear").val()
    filterBy=$("#filterBy").val()
    console.log(yearMonth)
     $.ajax({
        type: "GET",
        url: "/upload/get-bill-cycles-byfilter/",
        data: {'yearMonth':yearMonth,'filterBy':filterBy},
        success: function(response) {
                console.log('response',response)
                $('#importbody').html('')
                $('#importbody').html(response)
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


 function upload_b30(id,uploadb30){
    yearMonth=$("#monthYear").val()
    $.ajax({
        type: "GET",
        url: "/upload/get-upload-summery/",
        data: {'id':id,'yearMonth':yearMonth},
        success: function(response) {
            console.log('result');
            console.log('response', response["success"]);
            console.log('response', response.totalRouteDetail);
            //console.log('response', JSON.parse(response));
            if(response.success=='true'){
                $('#uploadId').val(uploadb30);
                $('#totalRoutesConsumers').text(response.totalRouteDetail+'/'+response.total_record);
                $('#totalDispatched').text(response.dispachedCount);
                $('#totalCompleted1').text(response.completeReading);
                $('#validatorOne').text(response.validate1Reading);
                $('#validatorTwo').text(response.validate2Reading);
                $('#hiddenV1').val(response.validate1Reading);
                $('#hiddenV2').val(response.validate2Reading);
                $('#pending').text(response.pending);
                $('#uploadSummery').modal('show');
            }
            else
                alert('Server Error!')
        },
        error: function(response) {
            alert('Server Error!')
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

$('#uploadB30_btn').click(function(){

    vl1=parseInt($('#validatorOne').text())
    vl2=parseInt($('#validatorTwo').text())

    if (vl1 >0 || vl2 > 0){
      bootbox.alert("<span class='center-block text-center'>First Validate all the records those, are in validation process !</span>");
      return false;
    }

    bootbox.confirm({
        title: "Validation",
        message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Are you sure you want to upload this Bill Cycle?<b>",
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
                    type: "GET",
                    url: "/upload/save-b30-table/",
                    data: {'id':$('#uploadId').val()},
                    success: function(response) {
                        if(response.success=='true'){
                            $('#uploadSummery').modal('hide');
                            refresh_upload()}
                        else
                            alert('Server Error!')
                    },
                    error: function(response) {
                        alert('Server Error!')
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
        }
    });




});

