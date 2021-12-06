var username = null;
var password = null;
var date = null;
var gare_depart = null;
var gare_arrivee = null;
var seatType = null;
var billet = null;
var available_voiture = null;
var datedepart = null;

function login(){
	if(username === null){
		username = $("[name='username']")[0].value;
		password = $("[name='password']")[0].value;
	}
	var form = {
		'username' : username,
		'password' : password
	};
	$.ajax({
		type: 'POST',
		url: '/login',
		data: form,
		success: function(response){
			$('.module').html(response);
			$('.module').addClass('module-after-login');
			$('.login-header').addClass('after-login');
			$('#datepicker-cashier').pickadate({
				min : new Date(),
				formatSubmit: 'yyyy/mm/dd',
 				hiddenName: true,
 				onSet: function( event ) {
 					if ( event.select ) {
 						$('#datepicker-cashier').prop('disabled', true);
 						getTrainOnDate(this.get('select', 'yyyy/mm/dd' ));
 					}
 				}
			});
		}
	});
}

// Functions for user
function getTrainOnDate(mdate){
	date = mdate;
	$.ajax({
		type: 'POST',
		url: '/getTrainsDate',
		data: {'date' : date},
		success: function(response){
			$('#trains-on-date').html(response);
		}
	});
}
function selectTrajet(jour, depart, arrivee){
	date = jour
	gare_depart = depart
	gare_arrivee = arrivee
	$.ajax({
		type: 'POST',
		url: '/getTimings',
		data: {
			'date' : date,
			'gare_depart': gare_depart,
			'gare_arrivee' : gare_arrivee
		},
		success: function(response){
			$('#trains-on-date button').prop('disabled', true);
			$('#timings-for-train').html(response);
		}
	});
}
function selectTiming(id_billet){
	billet = id_billet;
	$.ajax({
		type: 'POST',
		url: '/getBilletID',
		data: {
			'id_billet' : billet
		},
		success: function(response){
			$('#timings-for-train button').prop('disabled', true);
			available_voiture = response['available_voiture'];
			getSeats();
		}
	});
}
function getSeats(){
	$.ajax({
		type: 'POST',
		url: '/getAvailableSeats',
		data: {'available_voiture' : available_voiture},
		success: function(response){
			$('#available-seats').html(response);
		}
	});
}
function selectSeat(stype){
	seatType = stype;
	$.ajax({
		type: 'POST',
		url: '/getPrice',
		data: {
			'billet' : billet,
			'seatType' : seatType,
			'username' : username
			},
		success: function(response){
			$('#price-and-confirm').html(response);
		}
	});
}
function confirmBooking(){
	$.ajax({
		type: 'POST',
		url: '/insertBooking',
		data: {
			'id_billet' : billet,
			'username' : username,
			'seatType' : seatType
			},
		success: function(response){
			$('#available-seats button').prop('disabled', true);
			$('#price-and-confirm').html(response);
		}
	});
}

// Functions for manager
function viewBookedTickets(){
	$('#options button').prop('disabled', true);
	$('#manager-dynamic-1').html('<input id="datepicker-manager-1" placeholder="Pick a date">');
	$('#datepicker-manager-1').pickadate({
				formatSubmit: 'yyyy/mm/dd',
 				hiddenName: true,
 				onSet: function( event ) {
 					if ( event.select ) {
 						$('#datepicker-manager-1').prop('disabled', true);
 						getTrainsOnDate(this.get('select', 'yyyy/mm/dd' ));
 					}
 				}
	});
}
function getTrainsOnDate(mdate){
	date = mdate;
	$.ajax({
		type: 'POST',
		url: '/getTrainOnDate',
		data: {'date' : date},
		success: function(response){
			$('#manager-dynamic-2').html(response);
		}
	});
}
function selectBillet(id_billet){
	billet = id_billet;
	$.ajax({
		type: 'POST',
		url: '/getBookedWithBilletID',
		data: {'id_billet' : billet},
		success: function(response){
			$('#manager-dynamic-2 button').prop('disabled', true)
			$('#manager-dynamic-3').html(response);
		}
	});
}
function insertBillet(){
	$('#options button').prop('disabled', true);
	$.ajax({
		type: 'GET',
		url: '/fetchBilletInsertForm',
		success: function(response){
			$('#manager-dynamic-1').html(response);
			$('#datePicker-manager-2').pickadate({
				formatSubmit: 'yyyy/mm/dd',
 				hiddenName: true,
 				onSet: function( event ) {
 					if ( event.select ) {
 						datedepart = this.get('select', 'yyyy/mm/dd' );
 					}
 				}
			});
		}
	});
}
function filledBilletForm(){
	id_billet = $('[name="id_billet"]')[0].value
	id_train = $('[name="id_train"]')[0].value;
	prix = $('[name="prix"]')[0].value;
	g_depart = $('[name="g_depart"]')[0].value;
	g_arrivee = $('[name="g_arrivee"]')[0].value;
	h_depart = $('[name="h_depart"]')[0].value;

		$.ajax({
			type: 'POST',
			url: '/insertBilletInfo',
			data: {
				'id_billet' : id_billet,
				'id_train' : id_train,
				'prix' : prix,
				'g_depart' : g_depart,
				'g_arrivee' : g_arrivee,
				'h_depart' : h_depart,
				'j_depart' : datedepart,
			},
			success: function(response){
				$('#manager-dynamic-2').html(response);
			}
		});
	}
