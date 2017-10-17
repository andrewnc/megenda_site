$(document).ready(function(){
	var from_active = false;


	// Only connects on this page - although that is a problem because I bet there will be namespace issues between Agendas, 
	// I'm actually totally confident there are problems. Anyone on any agenda will have their thing advanced when someone
	// Clicks on a point anywhere.
	var socket = io.connect('http://' + document.domain + ':' + location.port);
	socket.on('connect', function() {
	    // we emit a connected message to let know the client that we are connected.
	    socket.emit('client_connected', {data: 'New client!'});
	});

	socket.on('new_active', function(data) {
		if(from_active){
			// Is true if the card was progressed from here, do nothing since we don't want to progress the agenda twice

		}else{
			var card_to_advance = $(".card[style='display: block;']").first();
			// This code makes sure that you don't get updates from other people's agendas, we will definitely have to fix this
			// When the site gets a lot of traffic, but for now I think we're going to be ok. 
			if("/view/" + data.data != window.location.pathname){
				// pass
			}else{
				advance_listner_card(card_to_advance);
			}
        	
		}
		from_active = false;
		
    });


	function push_active(point_id){
		$.ajax({
		  method: "POST",
		  url: "/view/active/" + point_id,
		})
		  .done(function( msg ) {
		    from_active = true;
		  });
	}

	// These two following functions need to be refactored - they have a TON of duplicated code and the logic flow isn't optimal. 
	// It'll take a bit of work, but I think it will be no problem. 

	function advance_listner_card(card_to_advance){
		var next = card_to_advance.next();
		if(next.length == 0){
			$(".card-container").children().first().toggle();

			var index = $(".card-container").children().first().children().eq(1).attr('class').split(" ")[1];

			$(".overview").removeClass('current-active');
			$("#overview_{0}".format(index)).addClass('current-active');

			card_to_advance.toggle();
		}else{
			card_to_advance.toggle();
			var index = $(next).children().eq(1).attr('class').split(" ")[1]

			$(".overview").removeClass('current-active');
			$("#overview_{0}".format(index)).addClass('current-active');

			next.toggle();
		}
	}	

	function advance_card(card_to_advance){
		var next = card_to_advance.next();
		if(next.length == 0){
			$(".card-container").children().first().toggle();

			var index = $(".card-container").children().first().children().eq(1).attr('class').split(" ")[1];
			push_active(index);

			$(".overview").removeClass('current-active');
			$("#overview_{0}".format(index)).addClass('current-active');

			card_to_advance.toggle();
		}else{
			card_to_advance.toggle();

			var index = $(next).children().eq(1).attr('class').split(" ")[1]
			push_active(index);

			$(".overview").removeClass('current-active');
			$("#overview_{0}".format(index)).addClass('current-active');


			next.toggle();
		}
	}
	$(".card").click(function(){
		advance_card($(this));

	})
})