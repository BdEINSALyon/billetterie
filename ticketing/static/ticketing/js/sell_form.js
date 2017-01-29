
$(function () {
    var $form = $('#sell-ticket-form');

    $form.find('#id_va_id').keydown(function(e){
        if(e.keyCode == 13){
            console.log('Search for VA identification ...');
            e.preventDefault();
        }
    })
});