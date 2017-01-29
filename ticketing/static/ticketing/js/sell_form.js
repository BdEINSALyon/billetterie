
$(function () {
    var $form = $('#sell-ticket-form');

    $form.find('#id_va_id').keydown(function(e){
        if(e.keyCode == 13){
            $form.addClass('loading-mask');
            $.post('/va/check', {code: $(this).val()}).done(function(result){
                $('#id_first_name').val(result.first_name);
                $('#id_last_name').val(result.last_name);
                $('#id_email').val(result.email);
            }).always(function(){
                $form.removeClass('loading-mask');
            });
            e.preventDefault();
        }
    })
});