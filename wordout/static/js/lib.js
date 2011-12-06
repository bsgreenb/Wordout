function load_data_to_modal(page){
    $('.label.notice').each(function(){
    	$(this).click(function(){
    		$.getJSON("/" + page + "/" + $(this).attr('id') + "/", {}, function(data){
    			if (data[0].success === true)
    			{						
    				$('table#clickDetail tbody').empty();
    				for (i=1; i< data.length; i++)
    				{
    					link = data[i].host_name + data[i].path_loc;
    					html = '<tr><td><a href="' + link + '">' + link + '</a></td><td>' + data[i].clicks + '</td></tr>';
    					$('#clickDetail tbody').append(html);

    				}
    				$('#detail-modal-from-dom').modal('show');				
    			}
    		});	
    	});
    }); 
}
