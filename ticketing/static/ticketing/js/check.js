$(function(){
    $('input').focus();
    $('a.code-input').click(function(e){
        $('input[type=text]:first').val($(this).data('code')).closest('form').submit();
        e.preventDefault();
    })
});