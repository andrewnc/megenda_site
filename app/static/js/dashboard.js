$(document).ready(function(){

    var getUrlParameter = function getUrlParameter(sParam) {
        var sPageURL = decodeURIComponent(window.location.search.substring(1)),
            sURLVariables = sPageURL.split('&'),
            sParameterName,
            i;

        for (i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');

            if (sParameterName[0] === sParam) {
                return sParameterName[1] === undefined ? true : sParameterName[1];
            }
        }
    };

    // Fancy format functoin
    if (!String.prototype.format) {
      String.prototype.format = function() {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function(match, number) { 
          return typeof args[number] != 'undefined'
            ? args[number]
            : match
          ;
        });
      };
    }
    var param = getUrlParameter('clicked');

    // populates the side box with info from the currently viewed agenda
    function get_side_box(uuid){
        // var uuid = $(this).attr('uuid');
        $.ajax({
            type: 'GET',
            url: '/agenda/'+uuid,
            success: function(results){
                $(".side-bar").show();
                var array_of_points = [];



                for (i in results['points']){
                    var st = "<ol>Name: {0}</ol>\n<ol>Content: {1}</ol>\n<ol>Current Active: {2}</ol>\n<ol>Duration: {3}</ol>".format(results['points'][i]['name'], results['points'][i]['content'], results['points'][i]['current_active'], results['points'][i]['duration']);
                    array_of_points.push(st);
                }

                var response = "<ol>Creator: {0}</ol>\n<ol>Date Created: {1}</ol><h3>Points</h3>\n<ul>\n{2}</ul>".format(results['created_by'], results['date_created'], array_of_points);
                

                $(".side-bar-name").html(results['name']);
                $(".side-bar-list").html(response);
                $(".side-bar-button").html("<a href='/add/point/{0}' class='btn btn-default'>Add point</a>".format(uuid))
            }
        });
    }

    if(param!=null){
        get_side_box(param);   
    }



	$(".delete").click(function(){
		return confirm("Are you sure you want to delete this agenda?");
	});

    // handles clicks on agenda names
    $(".agenda-name").click(function(){
        var uuid = $(this).attr('uuid');
        console.log(uuid);
        get_side_box(uuid);
        
    });
})