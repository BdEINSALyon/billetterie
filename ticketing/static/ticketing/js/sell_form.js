$(function () {
    var $form = $('form#sell-ticket-form');
    $form.find("select").focus();

    var last_va_checked = "";
    $form.find('#id_va_id').keydown(function (e) {
        if (e.keyCode === 13) {
            if(last_va_checked!==$(this).val()){
                last_va_checked = "";
                return;
            }
            $form.addClass('loading-mask');
            $.post('/va/check', {code: $(this).val()}).done(function (result) {
                if(result.tickets>0){
                    alert('danger', 'La carte VA a déjà un billet lié');
                    $form.find("input[type=text], textarea").val("");
                } else {
                    $('#id_first_name').val(result.first_name);
                    $('#id_last_name').val(result.last_name);
                    $('#id_email').val(result.email);
                }
            }).always(function () {
                $form.removeClass('loading-mask');
            });
            e.preventDefault();
            last_va_checked = $(this).val();
        }
    });

    var check_va_selling = function(){
        $form.find("input[type=text], textarea").val("");
        var mode = $form.find('input[type="radio"][name="entry"]:checked').data('selling')
        var $va = $form.find('input[name="va_id"]');
        if(mode == 'va_only') {
            $va.attr('required', true);
        } else {
            $va.removeAttr('required');
        }
        if(mode == 'no_va') {
            $va.closest('.form-group').hide();
        } else {
            $va.closest('.form-group').show();
        }
    };
    check_va_selling();
    $form.find('input[type="radio"][name="entry"]').change(check_va_selling);

    function alert(type, message){
        $('.alerts').html(
            '<div class="alert alert-'+type+'">'+'' +
            '<a class="close" data-dismiss="alert">×</a>'+
            '<span>' + message + '</span>'+
            '</div>');
        setTimeout(function(){
            $('.alerts').html('');
            if($('.swap').length>0){
                window.history.forward();
                window.location.reload();
            }
        }, 5000)
    }

    $form.submit(function (e) {
        var url = window.location.href; // the script where you handle the form input.

        $form.addClass('loading-mask');
        $.ajax({
            type: "POST",
            url: url,
            data: $form.serialize(),
            success: function (data) {
                console.log(data);
                if(data.success){
                    if(data.type == 'va'){
                        alert('success', 'Vente enregistrée, la carte VA sert de support pour le billet.');
                    } else {
                        alert('success', 'Vente enregistrée, le billet a été envoyé par email.');
                    }
                    $('.swap').hide();
                    $form[0].reset();
                    $form.find("select").focus();
                } else {
                    alert('danger', 'Erreur lors de l\'achat, la vente N\'EST PAS enregistrée. Raison : '+data.reason);
                }

            }
        }).always(function () {
            $form.removeClass('loading-mask');
        });

        e.preventDefault(); // avoid to execute the actual submit of the form.
    })
});