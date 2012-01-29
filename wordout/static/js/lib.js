$('a.close').live('click',function() {
    $(this).parent('div.alert-message').remove();
});
