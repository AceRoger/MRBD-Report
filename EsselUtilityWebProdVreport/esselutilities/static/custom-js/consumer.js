
$(function() {
    $(".active-me").removeClass("active");
    $('#import_menu').addClass("active");

   get_table_initilize('All');
});

//$( document ).ready(function() {
//    console.log( "ready!" );
//});

function get_table_initilize(route_code) {
console.log($('#billSchedule_id').val())
        var table = $('#consumer_tbl').dataTable({
            "processing": true,
            "serverSide": true,
            "destroy": true,
            "ajax": "/consumer/get-consumers-list/?route_code="+route_code+'&billSchedule_id='+$('#billSchedule_id').val(),
            "searching": true,
            "ordering": true,
            "paging": true,
            "columnDefs": [
                {"targets": 3, "orderable": false},
                {"targets": 4, "orderable": false},
                {"targets": 5, "orderable": false},
                {"targets": 6, "orderable": false},
                {"targets": 7, "orderable": false},
            ]
        });
 }

 $("#routeCodeSelect").change(function() {
  //alert( "Handler for .change() called." );
    rout_code=$("#routeCodeSelect").val()
    get_table_initilize(rout_code)
});

 function viewConsumer(id){
      $.ajax({
        type: "GET",
        url: "/consumer/get-consumer-details/",
        data: {'id':id},
        success: function(response) {
            if (response.success=='true'){
                  $('#billCycle').text(response.bill_cycle);
                  $('#routeCode').text(response.route);
                  $('#consumerName').text(response.name);
                  $('#consumerNo').text(response.consumer_no);
                  $('#consumerAddress').text(response.address);
                  $('#dtcNo').text(response.dtc);
                  $('#poleNo').text(response.pole_no);
                  $('#meterNo').text(response.meter_no);
                  $('#feederCode').text(response.feeder_code);
                  $('#feederName').text(response.feeder_name);

                  $('#connection_status').text(response.connection_status);
                  $('#killowatt').text(response.killowatt);

                  $('#viewConsumerModel').modal('show');
            }
            else{
            alert('Server Error !')
            }

        },
        error: function(response) {
            console.log('error');
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