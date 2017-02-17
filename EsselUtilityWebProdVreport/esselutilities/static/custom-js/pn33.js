
$(function() {

    $(".active-me").removeClass("active");
    $('#import_menu').addClass("active");


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


function refresh(){
    yearMonth=$("#monthYear").val()
    console.log(yearMonth)
     $.ajax({
        type: "GET",
        url: "/consumer/get-bill-cycles/",
        data: {'yearMonth':yearMonth},
        success: function(response) {
                console.log('response',response)
                $('#importbody').html('');
                $("#filterBy").val('All');
                $('#importbody').html(response);

                $("#lbl_totalRecord").text($('#totalRecord').val()+' Total')
                $("#lbl_totalCompleted").text($('#totalCompleted').val())
                $("#lbl_totalNotStarted").text($('#totalNotStarted').val())
                $("#lbl_totalStarted").text($('#totalStarted').val())
                $("#lbl_totalFailed").text($('#totalFailed').val())

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
    refresh()
});


$("#filterBy").change(function(){
    console.log('======================================>')
    yearMonth=$("#monthYear").val()
    filterBy=$("#filterBy").val()
    console.log(yearMonth)
     $.ajax({
        type: "GET",
        url: "/consumer/get-bill-cycles-byfilter/",
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





 function import_pn33(id){
    $.ajax({
        type: "GET",
        url: "/consumer/import-pn33/",
        data: {'id':id},
        success: function(response) {
            console.log('result');
            console.log('response', response);
            if(response.success=='true')
                //location.reload();
                refresh()
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







