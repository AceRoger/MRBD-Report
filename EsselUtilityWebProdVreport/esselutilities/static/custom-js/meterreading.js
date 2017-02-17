
$(function() {

    $(".active-me").removeClass("active");
    $('#upload_menu').addClass("active");

   get_table_initilize('All','All','All');
});

//$( document ).ready(function() {
//    console.log( "ready!" );
//});

function get_table_initilize(route_code,reading_status,meterStatus) {
console.log($('#billCycle_id').val())
        var table = $('#reading_tbl').dataTable({
            "processing": true,
            "serverSide": true,
            "destroy": true,
            "ajax": "/upload/get-reading-list/?route_code="+route_code+'&billSchedule='+$('#billSchedule_id').val()+'&readingStatus='+reading_status+'&meterStatus='+meterStatus,
            "searching": true,
            "ordering": true,
            "paging": true,
            "columnDefs": [
                {"targets": 4, "orderable": false},
                {"targets": 5, "orderable": false},
                {"targets": 6, "orderable": false},
                {"targets": 7, "orderable": false},
            ]
        });
 }

 $("#routeCodeSelect").change(function() {
    rout_code=$("#routeCodeSelect").val()
    readingStatus=$("#readingStatus").val()
    meterStatus=$("#meterStatusSelect").val()
    console.log(meterStatus)
    get_summery()
    get_table_initilize(rout_code,readingStatus,meterStatus)
});

 $("#meterStatusSelect").change(function() {
    rout_code=$("#routeCodeSelect").val()
    readingStatus=$("#readingStatus").val()
    meterStatus=$("#meterStatusSelect").val()
    console.log(meterStatus)
    get_summery()
    get_table_initilize(rout_code,readingStatus,meterStatus)
});


$("#readingStatus").change(function() {
    rout_code=$("#routeCodeSelect").val()
    readingStatus=$("#readingStatus").val()
    meterStatus=$("#meterStatusSelect").val()
    get_summery()
    get_table_initilize(rout_code,readingStatus,meterStatus)
});


function get_summery(){
billSchedule=$('#billSchedule_id').val()
route_code=$("#routeCodeSelect").val()
meterStatus=$("#meterStatusSelect").val()

    $.ajax({
        type: "GET",
        url: "/upload/get-upload-summery-by-route/",
        data: {'billSchedule':billSchedule,'route_code':route_code,'meterStatus':meterStatus,'meterStatus':meterStatus},
        success: function(response) {
            if(response.success=='true'){
               /* $('#lbl_totalRecord').text(response.total_record+' Total Reading');
                $('#lbl_totalCompleted').text(response.totalMeterReading+' Completed');
                $('#lbl_totalNotStarted').text(response.pending+' Pending');*/
                $('#lbl_totalRecord').text(response.total_record);
                $('#lbl_totalCompleted').text(response.totalMeterReading);
                $('#lbl_totalNotStarted').text(response.pending);
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



function test(){
    alert('vkmchandel');
}



// $('#routeCodeSelect').click(function(){
// alert('vkmchandel');
// });