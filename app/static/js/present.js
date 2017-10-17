$(document).ready(function(){
	var num_finished = 0;
	var num_off_topic = 0;

// I need to rename current-active to current_active... oops

	var socket = io.connect('http://' + document.domain + ':' + location.port);
	socket.on('connect', function() {
	    // we emit a connected message to let know the client that we are connected.
	    socket.emit('client_connected', {data: 'New client!'});
	});

	socket.on('new_active', function(data) {
		// check and see if we have update the point yet
		if($(".current-active").attr("id").replace("overview_", "") != data.id){
			// don't update if the push comes from a different meeting - not robust, but it works for now
			if("/view/" + data.data != window.location.pathname){
				// pass
			}else{
				advance_card(data.id, is_listner=true);
			}
		}else{

		}
    });


	function push_active(point_id){
		$.ajax({
		  method: "POST",
		  url: "/view/active/" + point_id,
		})
		  .done(function( msg ) {
		  	//pass
		  });
	}


	function advance_card(index, is_listner = false){
		if(is_listner){
			index = index -1;
			index = index.toString();
		}
		index = parseInt(index);
		var next = $("#overview_{0}".format(index+1));
		if(next.length == 0){
			// Go back to the first element in the list
			index = parseInt($(".overview").first().attr("id").replace("overview_",""));
			if(!is_listner){
				push_active(index);
			}
			
			$(".overview").removeClass('current-active');
			$("#overview_{0}".format(index)).addClass('current-active');

		}else{
			$(".overview").removeClass('current-active');
			next.addClass('current-active');
			if(!is_listner){
				push_active(index+1);
			}
		}
	}

	$(document).keypress(function(event){
		var pressed = String.fromCharCode(event.which);
	  if(pressed == "f"){
	  	num_finished += 1;
	  } else if (pressed == "d"){
	  	num_off_topic += 1;
	  }
	  console.log(num_finished);
	  if(num_finished > 3){
	  	$("body").css("background-color", "red");
	  	alert("You're finished, move on!");
	  }

	  if(num_off_topic > 3){
	  	$("body").css("background-color", "yellow");
	  	alert("You're off topic, back on track!");
	  }
	});


	$(".advance_point").unbind('click').bind('click', function(){
		var index = $(".current-active").attr('id').replace("overview_", "");
		advance_card(index);
	})
})