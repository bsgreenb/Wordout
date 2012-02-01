// those two functions are used for enable_or_disable on both sharer.html and action_type_page.html

function set_ls_from_checkbox(name){ //used for edit redirect link, disable, enable

    var element = '#' + name;
    if ($(element).val() != 'ALL')
    {
        $(element).val('');

        var values = '';
        $('.checkbox:checked').each(function(){
            values += $(this).val() + ',';
        });
        $(element).val(values);
    }
}

function enable_or_disable(url, name, csrf_token){
    var element = '#' + name;

    $.post(url,{
            ls: $(element).val(),
            csrfmiddlewaretoken: csrf_token
        },
        function(data){
            if (data['status'] == 'OK')
            {
                $('.checkbox:checked').each(function(){
                    $(this).parent().parent().find('.enable').html(data['enable_text']);
                });
            }
        }, "json");
}