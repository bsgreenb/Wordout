function load_data_to_modal(page) {
    $('.label.notice').each(function(){
        $(this).click(function(){
            $.getJSON("/" + page + "/" + $(this).attr('id') + "/", {}, function(data){
                if (data.success === true)
                {
                    $('table#clickDetail tbody').empty();
                    for (i=0; i< data['response'].length; i++)
                    {
                        link = data['response'][i].referrer;
                        html = '<tr><td><a href="' + link + '">' + link + '</a></td><td>' + data['response'][i].clicks + '</td></tr>';
                        $('#clickDetail tbody').append(html);

                    }
                    $('#detail-modal-from-dom').modal('show');
                }
            });
        });
    });
}