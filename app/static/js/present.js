$(document).ready(function(){
	var from_active = false;

	var socket = io.connect('http://' + document.domain + ':' + location.port);
	socket.on('connect', function() {
	    // we emit a connected message to let know the client that we are connected.
	    socket.emit('client_connected', {data: 'New client!'});
	});

	socket.on('new_active', function() {
		if(from_active){
			// Is true if the card was progressed from here

		}else{
			var block = $(".card[style='display: block;']").first();
        	advance_card_from_other(block);

		}
		from_active = false;
		
    });

	

	function push_active(point_id){
		$.ajax({
		  method: "POST",
		  url: "/view/active/" + point_id,
		})
		  .done(function( msg ) {
		    // console.log( "Data Saved: " + msg );
		    // $(".current_point").text(msg);
		    from_active = true;
		  });
	}

	function advance_card_from_other(me){
		var next = me.next();
		if(next.length == 0){
			$(".card-container").children().first().toggle();
			// push_active($(".card-container").children().first().children().eq(1).attr('class').split(" ")[1]);
			me.toggle();
		}else{
			me.toggle();
			// push_active($(next).children().eq(1).attr('class').split(" ")[1]);
			next.toggle();
		}
	}	

	function advance_card(me){
		var next = me.next();
		if(next.length == 0){
			$(".card-container").children().first().toggle();
			push_active($(".card-container").children().first().children().eq(1).attr('class').split(" ")[1]);
			me.toggle();
		}else{
			me.toggle();
			push_active($(next).children().eq(1).attr('class').split(" ")[1]);
			next.toggle();
		}
	}
	$(".card").click(function(){
		advance_card($(this))
		// Set current active point
	})
})