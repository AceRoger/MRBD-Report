
//function for change route according to bill cycle
//$('#billCycle').change(function() {
//    getRoute('#billCycle', '#routeDetail');
//});


$(function() {
    $(".active-me").removeClass("active");
    $('#system_user_menu').addClass("active");
    initMap()

});


function getRoute(billCycleDropDown, routeDropDown) {
    id = $(billCycleDropDown).val();
    $.ajax({
        type: 'POST',
        url: '/meterreader/get-route-detail/',
        data: {
            'bill_cycle_code': id
        },
        success: function(response) {
            console.log('response', response);
            $(routeDropDown).html('');
            $.each(response.route_list, function(index, item) {
                $(routeDropDown).append(item);
            });
        },
        error: function(response) {
            alert("Error!");
        },
    });
}

function get_bill_cycle(){
$.ajax({
        type: 'POST',
        url: '/meterreader/get-bill-cycle/',
        data:{
            'monthYear':$("#monthYear").val(),
            'mr_id':$("#mr_id").val()
        },
        success: function(response) {
            console.log('response', response.billCycle);
            $("#billCycle").html("");
            $("#billCycle").append("<option value=''>Select Bill Cycle</option>");
            $.each(response.billCycle, function (index, item) {
                data = '<option value="'+ item.id +'">'+ item.billCycle +'</option>'
                $("#billCycle").append(data);
            });
        },
        error: function(response) {
            alert("Error!");
        },
    });
}

function get_routes(){
$.ajax({
        type: 'POST',
        url: '/meterreader/get-route-for-track/',
        data:{
            'billCycle':$("#billCycle").val(),
            'monthYear':$("#monthYear").val(),
            'mr_id':$("#mr_id").val()
        },
        success: function(response) {
            console.log('response', response.billCycle);
            $("#routeDetail").html("");
            $("#routeDetail").append("<option value=''>Select Route</option>");
            $.each(response.billCycle, function (index, item) {
                data = '<option value="'+ item.id +'">'+ item.route +'</option>'
                $("#routeDetail").append(data);
            });
        },
        error: function(response) {
            alert("Error!");
        },
    });
}

var locations=""

function get_route_path(){
//alert('chandel');
$.ajax({
        type: 'POST',
        url: '/meterreader/get-route-path/',
        data:{
            'billCycle':$("#billCycle").val(),
            'monthYear':$("#monthYear").val(),
            'route':$("#routeDetail").val(),
            'mr_id':$("#mr_id").val()
        },
        success: function(response) {
            console.log('response', response);

            if(response.success='true'){
                locations=response.locations
                lastLocation = locations[locations.length-1];
                console.log('first:',locations[0].longitude)
                //initMap_dynamic(locations[0],lastLocation,locations)
                initialize(locations)
            }
            else{
                bootbox.alert("<span class='center-block text-center'>There are no GPS locations found for this route besed on readings!</span>");
                initMap()
            }

        },
        error: function(response) {
            alert("Error!");
        },
    });
}


function get_map(){
var selectedMode = document.getElementById('mode').value;
 if(selectedMode=='Basic')
    initialize(locations)
 else if(selectedMode=='Path'){
    lastLocation = locations[locations.length-1];
    initMap_dynamic(locations[0],lastLocation,locations)
}
}


function initMap_dynamic(source,destin,locations) {
        var directionsDisplay = new google.maps.DirectionsRenderer;
        var directionsService = new google.maps.DirectionsService;
        var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 14,
          center: {lat: 18.5204, lng: 73.8567} //Map center Nagpur
        });

        directionsDisplay.setMap(map);

        calculateAndDisplayRoute_dynamic(map,directionsService, directionsDisplay,source,destin,locations);
        /*document.getElementById('mode').addEventListener('change', function() {
          calculateAndDisplayRoute_dynamic(map,directionsService, directionsDisplay,source,destin,locations);
        });*/


        var infowindow = new google.maps.InfoWindow();
         for (i = 0; i < locations.length-1; i++) {
                calculateAndDisplayRoute_dynamic(map,directionsService, directionsDisplay,locations[i],locations[i+1],locations);
           }

      for (i = 1; i < locations.length-1; i++) {
            console.log('locations[i].latitude',locations[i].latitude)
            marker = new google.maps.Marker({
            position: new google.maps.LatLng(parseFloat(locations[i].latitude),parseFloat(locations[i].longitude)),
            map : map
            });
           google.maps.event.addListener(marker, 'click', (function(marker, i) {
            return function() {
            infowindow.setContent('vikram-'+str(i));
            infowindow.open(map, marker);
            }
          })(marker, i));
      }
    }

function calculateAndDisplayRoute_dynamic(map,directionsService, directionsDisplay,source,destin,locations) {
        var selectedMode = document.getElementById('mode').value;
        var slati=parseFloat(source.latitude)
        var slong=parseFloat(source.longitude)
        var dlati=parseFloat(destin.latitude)
        var dlong=parseFloat(destin.longitude)

         //console.log(TravelMode[selectedMode])

        directionsService.route({
          origin: {lat: slati, lng: slong},  // Haight.
          destination: {lat: dlati, lng: dlong},

          // Note that Javascript allows us to access the constant
          // using square brackets and a string value as its
          // "property."

          travelMode: google.maps.TravelMode["WALKING"]
        }, function(response, status) {
          if (status == 'OK') {
            directionsDisplay.setDirections(response);
          } else {
            window.alert('Directions request failed due to ' + status);
          }
        });
   }


function initMap() {
        var directionsDisplay = new google.maps.DirectionsRenderer;
        var directionsService = new google.maps.DirectionsService;
        var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 14,
          center: {lat:26.07, lng: 85.27} //Map center Nagpur


        });
        directionsDisplay.setMap(map);

       /* calculateAndDisplayRoute(directionsService, directionsDisplay);
        document.getElementById('mode').addEventListener('change', function() {
          calculateAndDisplayRoute(directionsService, directionsDisplay);
        });*/
      }

function calculateAndDisplayRoute(directionsService, directionsDisplay) {
        var selectedMode = document.getElementById('mode').value;
        directionsService.route({

          //origin: {lat: 20.9374, lng: 77.7796},  // Haight.
          //destination: {lat: 20.8598, lng: 77.7368},

          origin: {lat: 20.9374, lng: 77.7796},  // Haight.
          destination: {lat: 20.8598, lng: 77.7368},

          // Note that Javascript allows us to access the constant
          // using square brackets and a string value as its
          // "property."
          travelMode: google.maps.TravelMode[selectedMode]
        }, function(response, status) {
          if (status == 'OK') {
            directionsDisplay.setDirections(response);
          } else {
            window.alert('Directions request failed due to ' + status);
          }
        });
      }





//var MapPoints = '[{"address":{"address":"plac Grzybowski, Warszawa, Polska","lat":"52.2360592","lng":"21.002903599999968"},"title":"Warszawa"},{"address":{"address":"Jana Paw\u0142a II, Warszawa, Polska","lat":"52.2179967","lng":"21.222655600000053"},"title":"Wroc\u0142aw"},{"address":{"address":"Wawelska, Warszawa, Polska","lat":"52.2166692","lng":"20.993677599999955"},"title":"O\u015bwi\u0119cim"}]';

var MY_MAPTYPE_ID = 'custom_style';

function initialize(locations) {

    if (jQuery('#map').length > 0) {

        //var locations = jQuery.parseJSON(MapPoints);

        window.map = new google.maps.Map(document.getElementById('map'), {
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            scrollwheel: false
        });

        var infowindow = new google.maps.InfoWindow();
        var flightPlanCoordinates = [];
        var bounds = new google.maps.LatLngBounds();

        for (i = 0; i < locations.length; i++) {
            marker = new google.maps.Marker({
                position: new google.maps.LatLng(locations[i].latitude, locations[i].longitude),
                map: map
            });
            flightPlanCoordinates.push(marker.getPosition());
            bounds.extend(marker.position);

            /*google.maps.event.addListener(marker, 'click', (function (marker, i) {
                return function () {
                    infowindow.setContent(locations[i]['title']);
                    infowindow.open(map, marker);
                }
            })(marker, i));*/
            }

            map.fitBounds(bounds);

            var flightPath = new google.maps.Polyline({
                map: map,
                path: flightPlanCoordinates,
                strokeColor: "#FF0000",
                strokeOpacity: 1.0,
                strokeWeight: 2
            });

        }
       google.maps.event.addDomListener(window, 'load', initialize);
    }
