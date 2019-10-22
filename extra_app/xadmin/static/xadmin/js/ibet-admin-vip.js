$(document).ready(function () {
    var csrftoken = $.cookie("csrftoken")
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    $("#min_date").datepicker();
    $("#max_date").datepicker();
    var minDate = $('#min_date').val();
    var maxDate = $('#max_date').val();

    var vip_table = $('#vip_table').DataTable({
        "serverSide": true,
        "searching": true,
        "ajax": {
            type: 'GET',
            url: vip_url,
            data: {
                'type': 'getVIPInfo',
                'system': 'vip_admin',
                'minDate': function () { return minDate; },
                'maxDate': function () { return maxDate; },
            },
        },
        columns: [
            { data: 'player_id' },
            { data: 'username' },
            { data: 'status' },
            { data: 'player_segment' },
            { data: 'country' },
            { data: 'address' },
            { data: 'phone_number' },
            { data: 'email_verified' },
            { data: 'phone_verified' },
            { data: 'id_verified' },
            { data: 'affiliate_id' },
            { data: 'ggr' },
            { data: 'turnover' },
            { data: 'deposit' },
            { data: 'deposit_count' },
            { data: 'ave_deposit' },
            { data: 'withdrawal' },
            { data: 'withdrawal_count' },
            { data: 'bonus_cost' },
            { data: 'ngr' },
        ],

        dom: 'B<ftilp>',
        buttons: [
            'csv',
        ],
        "language": {
            "info": " _START_ - _END_ of _TOTAL_",
            "infoEmpty": " 0 - 0 of 0",
            "infoFiltered": "",
            "paginate": {
                "next": '<button type="button" class="btn default" style="border:solid 1px #bdbdbd;">></button>',
                "previous": '<button type="button" class="btn default" style="border:solid 1px #bdbdbd;"><</button>'
            },
            "lengthMenu": "_MENU_",
        },
    });

//    $(".dt-buttons .buttons-csv").text("Export");
//
//    $('#min_date, #max_date').change(function () {
//        minDate = $('#min_date').val();
//        maxDate = $('#max_date').val();
//        minDate = formatStringToDate(minDate);
//        maxDate = formatStringToDate(maxDate);
//        vip_table.draw();
//    });
//    function formatStringToDate(date) {
//        if (date.length === 0) {
//            return date;
//        }
//        var parts = date.split('/');
//        date = parts[2] + '-' + parts[0] + '-' + parts[1];
//        return date;
//    }
});