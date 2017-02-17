
function searchMr(urlSearch){
    if( $("#searchTxtDispatchModal").val().length > 3 || $("#searchTxtDispatchModal").val().length == 0){
        $.ajax({
            type: "POST",
            url: "/dispatch/search-mr/",
            // url: urlSearch,
            data: {
                    'searchTxtDispatchModal':$('#searchTxtDispatchModal').val(),
                    'current_month':$("#current_month").val(),
                    },
            success: function(response) {
                    $('#searchMrID').html('');
                    $('#searchMrID').html(response);
            },
            error: function(response) {
                bootbox.alert("error");
                console.log('response', response);
            },
            beforeSend: function() {
            },
            complete: function() {}
        });
    }
}




function assignmr() {
    if ($('input:radio:checked').length > 0){
        $.ajax({
            type: "POST",
            url: '/dispatch/assign-mr/',
            data: $('#mrassignform').serialize(),
            success: function(response) {
                $("#history").modal('hide');
                window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;

            },
            error: function(response) {
                bootbox.alert('An unexpected error occured!');
            },
            beforeSend: function() {
            },
            complete: function() {
            }
        });
    }else{
        bootbox.alert("Please select a Meter reader!");
        return false;
    }


}







function get_mrdeatils(id){
    $.ajax({
        type: "POST",
        url: '/dispatch/get-mr/',
        data : $('#mrdetailsform'+id).serialize(),
        success: function(data) {
            $("#modalbody").html(data);
            $("#billcyclecode").html($("#billcyclecode1").val())
            $("#routecode").html($("#routecode1").val())
            // $("#end_date").html($("#end_date1").val())
             $("#history").modal('show');

            // console.log('response', response);
        },
        error: function(response) {
            bootbox.alert("cant save");
        },
        beforeSend: function() {
        },
        complete: function() {
        }
    });
}




function assign_samemr(id){
    $.ajax({
        type: "GET",
        url: '/dispatch/get-samemr/'+id,
        data : {
                    //'csrfmiddlewaretoken': $('#csrf input').val(),
                    'route_id': id,
                },
        success: function(data) {
            $("#modalbody").html(data);
        },
        error: function(response) {
            bootbox.alert("cant save");
        },
        beforeSend: function() {
        },
        complete: function() {
        }
    });
}


function get_mrdeatils_revisit(id){
    $.ajax({
        type: "POST",
        url: '/dispatch/get-mr-revisit/',
        data : $('#mrdetailsform'+id).serialize(),
        success: function(data) {
            $("#modalbody").html(data);
            $("#billcyclecode").html($("#billcyclecode1").val())
            $("#routecode").html($("#routecode1").val())
            // $("#end_date").html($("#end_date1").val())
             $("#history").modal('show');

            // console.log('response', response);
        },
        error: function(response) {
            bootbox.alert("cant save");
        },
        beforeSend: function() {
        },
        complete: function() {
        }
    });
}


function get_mrdeatils_revisit_list(id){
    $.ajax({
        type: "POST",
        url: '/dispatch/get-mr-revisit-list/',
        data : $('#mrdetailsformrevisit'+id).serialize(),
        success: function(data) {
            $("#modalbody").html(data);
            $("#billcyclecode").html($("#billcyclecode1").val())
            $("#routecode").html($("#routecode1").val())
            // $("#end_date").html($("#end_date1").val())
             $("#history").modal('show');

             console.log('response', response);
        },
        error: function(response) {
            bootbox.alert("cant save");
        },
        beforeSend: function() {
        },
        complete: function() {
        }
    });
}



function searchMrrevisit(urlSearch){
    if( $("#searchTxtDispatchModal").val().length > 3 || $("#searchTxtDispatchModal").val().length == 0){
        $.ajax({
            type: "POST",
            url: "/dispatch/search-mr-revisit/",
            // url: urlSearch,
            data: {
                    'searchTxtDispatchModal':$('#searchTxtDispatchModal').val(),
                    'current_month':$("#current_month").val(),
                    },
            success: function(response) {
                    $('#searchMrID').html('');
                    $('#searchMrID').html(response);
            },
            error: function(response) {
                bootbox.alert("error");
                console.log('response', response);
            },
            beforeSend: function() {
            },
            complete: function() {}
        });
    }
}



function assign_samemr_revisit(id){
    $.ajax({
        type: "GET",
        url: '/dispatch/get-samemr-revisit/'+id,
        data : {
                    //'csrfmiddlewaretoken': $('#csrf input').val(),
                    'route_id': id,
                },
        success: function(data) {
            $("#modalbody").html(data);
        },
        error: function(response) {
            bootbox.alert("cant save");
        },
        beforeSend: function() {
        },
        complete: function() {
        }
    });
}









function assignmrrevisit() {
    if ($('input:radio:checked').length > 0){
        $.ajax({
            type: "POST",
            url: '/dispatch/assign-mr-revisit/',
            data: $('#mrassignform').serialize(),
            success: function(response) {
                $("#history").modal('hide');
                window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;

            },
            error: function(response) {
                bootbox.alert("An unexpected error occured!");
            },
            beforeSend: function() {
            },
            complete: function() {
            }
        });
    }else{
        bootbox.alert("Please select a Meter reader!");
        return false;
    }


}

function do_deassign(id){
    // var r = confirm("Are you sure you want to deassign this route!");
    bootbox.confirm({
    title: "Deassign MR?",
    message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Are you sure you want to deassign this route!!<b>",
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
                url: '/dispatch/deassign-mr/',
                data : $('#mrdetailsform'+id).serialize(),
                success: function(response) {
                    bootbox.alert(" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Successfully deassigned the Route")
                    // window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;
                },
                error: function(response) {
                    bootbox.alert("An unexpected error occured!");
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


function do_deassign_revisit(id){
    // var r = confirm("Are you sure you want to deassign this route!");
    bootbox.confirm({
    title: "Deassign MR?",
    message: "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Are you sure you want to deassign this MR!!<b>",
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
                url: '/dispatch/deassign-mr-revisit/',
                data : $('#mrdetailsformrevisit'+id).serialize(),
                success: function(response) {
                    bootbox.alert(" &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Successfully deassigned the MR")
                    // window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;
                },
                error: function(response) {
                    bootbox.alert("An unexpected error occured!");
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

function searchEmail(inputVal){
    $('#meter_reader').find('tr').each(function(index, row)
    {
        var allCells = $(row).find('td');
        if(allCells.length > 0)
        {
            var found = false;
            allCells.each(function(index, td)
            {
                if(index == 3)
                {
                    var regExp = new RegExp(inputVal, 'i');
                    if(regExp.test($(td).text()))
                    {
                        found = true;
                        return false;
                    }
                }
            });
            if(found == true)$(row).show();else $(row).hide();
        }
    });
}

var table = null;

$(document).ready(function(){
   $("#searchTxt").keyup(function(){
        $(".testVal").each(function(){
            var count = $(this).attr("id");
            if(count.indexOf($("#searchTxt").val()) !== -1)
                $(this).show();
            else
                $(this).hide();
        });
    });



   $("#searchTxtroute").keyup(function(){
        $(".testVal").each(function(){
            var count = $(this).attr("id");
            if(count.indexOf($("#searchTxtroute").val()) !== -1)
                $(this).show();
            else
                $(this).hide();
        });
    });








   $(function(){
        $(".active-me").removeClass("active");
        $('#dispatch_menu').addClass("active");
    });

   table = $('#table-consumer-list').dataTable({
            "processing": true,
            "searching": true,
            "ordering": true,
            "paging": true,
            "distroy":true,
            "columnDefs": [
                {"targets": 3, "orderable": false},
                {"targets": 4, "orderable": false},
                {"targets": 5, "orderable": false},
                {"targets": 6, "orderable": false},
            ]
        });

});

$("#filterBy").change(function(){
    filterBy=$("#filterBy").val()
     $.ajax({
        type: "POST",
        url: "/dispatch/get-jobcard-byfilter/",
        data: {
                'filterBy':filterBy,
                'currentmonth':$('#monthYear').val()
                },
        // data:$('#filterjobcard').serialize(),
        success: function(response) {
                console.log('response')
                $('#dispatchBody').html('');
                $('#dispatchBody').html(response);
        },
        error: function(response) {
            bootbox.alert('error');
            console.log('response', response);
        },
        beforeSend: function() {

        },
        complete: function() {}
    });
});

$("#monthYear").change(function(){
    monthYear=$("#monthYear").val()
    url = "/dispatch/get-jobcard/"+ monthYear;
    window.location.href = url;
});

function refreshh(){
window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;
    }

// function refresh() {
//     alert('hi');
//     $.ajax({
//         type: "POST",
//         url: '/dispatch/refresh/',
//         // data: $('#mrassignform').serialize(),
//         success: function(response) {
//             $("#history").modal('hide');
//             window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;

//         },
//         error: function(response) {
//             bootbox.alert("An unexpected error occured!");
//         },
//         beforeSend: function() {
//         },
//         complete: function() {
//         }
//     });
// }

// }






function toggleCheck(source) {
    console.log($(source).is(':checked'));

    if ($(source).is(':checked'))
        $('.checker span').addClass("checked");
    else
        $('.checker span').removeClass("checked");
    $('input[name="consumer"]').each(function(){
        // console.log($(this).prop('checked'));
        $(this).prop('checked',$(source).is(':checked'));
    });
  // checkboxes = document.getElementsByName('consumer');
  // for(var i=0, n=checkboxes.length;i<n;i++) {
  //   checkboxes[i].checked = source.checked;
  // }
}

 $("#selectRoute").change(function() {
  //alert( "Handler for .change() called." );
    rout_code=$("#selectRoute").val()
    month=$("#month").val()
    billcycle=$("#billcycle").val()
    $.ajax({
        type: "POST",
        url: "/dispatch/get-revisit-byfilter/",
        data: {
                'rout_code':rout_code,
                'month':month,
                'billcycle':billcycle,

                },
        // data:$('#filterjobcard').serialize(),
        success: function(response) {
                console.log('response')
                $('#revisitBody').html('');
                $('#revisitBody').html(response);
                var table = $('#table-consumer-listt').dataTable({
                    "processing": true,
                    "searching": true,
                    "ordering": true,
                    "paging": true,
                    "columnDefs": [
                        {"targets": 3, "orderable": false},
                        {"targets": 4, "orderable": false},
                        {"targets": 5, "orderable": false},
                        // {"targets": 7, "orderable": false},
                    ]
                }).fnDraw();
        },
        error: function(response) {
            bootbox.alert('error');
            console.log('response', response);
        },
        beforeSend: function() {

        },
        complete: function() {}
    });
});

function assignmrrevisitlist() {
    if ($('input:radio:checked').length > 0){
        $.ajax({
            type: "POST",
            url: '/dispatch/assign-mr-revisit-list/',
            data: $('#mrassignform').serialize(),
            success: function(response) {
                $("#history").modal('hide');
                window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;

            },
            error: function(response) {
                bootbox.alert("An unexpected error occured!");
            },
            beforeSend: function() {
            },
            complete: function() {
            }
        });
    }else{
        bootbox.alert("Please select a Meter reader!");
        return false;
    }

}

function refresh() {
        current_month=$("#current_month").val()
        $.ajax({
            type: "POST",
            url: '/dispatch/refreshmrinfo/',
            data:{
                'current_month':current_month,

                },

            success: function(response) {
                window.location.href = window.location.protocol +'//'+ window.location.host + window.location.pathname;

            },
            error: function(response) {
                bootbox.alert("An unexpected error occured!");
            },
            beforeSend: function() {
            },
            complete: function() {
            }
        });
   


}
// function copyPrevMessage(){
// //alert("Schedule is Allready Copied from previous Month");
// bootbox.alert("<span class='center-block text-center'>Schedule is Allready Copied from previous Month!</span>",function(){
//     location.reload();
//     });
