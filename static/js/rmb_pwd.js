$.getScript( "https://cdnjs.cloudflare.com/ajax/libs/jquery-cookie/1.4.1/jquery.cookie.min.js", function( data, textStatus, jqxhr ) {
    $(document).ready(function() {
        $("#id_username").val($.cookie('username'));
        $("#id_password").val($.cookie('password'));
        if ($.cookie('remember') == "true") {
            $("#id_remember_me").prop('checked', true);
        } 
        $("#login-form").submit(function() {
            if ($("#id_remember_me").prop('checked')) {
                $.cookie('username', $("#id_username").val());
                $.cookie('password', $("#id_password").val());
                $.cookie('remember', "true");
            } else {
                $.removeCookie('username');
                $.removeCookie('password');
                $.removeCookie('remember');
            }
            return true;
        });
    });
  });

