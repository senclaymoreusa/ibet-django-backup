$(document).ready(function () {

    var vip_table = $('#vip_table').DataTable({
        "serverSide": true,
        "searching": true,
        "ordering": false,
        "dom": '<<t>Bpil>',
        "ajax": {
            type: 'GET',
            url: vip_url,
            data: {
                'type': 'getVIPInfo',
                'system': 'vip_admin',
                'segment': function() {var segment=$('#segmentation_filter :selected').val(); return segment;},
                'minDate': function () { return $('#min_date').val(); },
                'maxDate': function () { return $('#max_date').val(); },
            },
        },

        columns: [
            { data: 'player_id',
              "render": function(data, type, row, meta){
                if(type === 'display'){
                    data = '<a href=' + user_link + data + '>' + data+ '</a>';
                }
                return data;
             }},
            { data: 'username',
              "render": function(data, type, row, meta){
                if(type === 'display'){
                    data = '<a href=' + user_link + row['player_id'] + '>' + data + '</a>';
                }
                return data;
             }},
            { data: 'status' },
            { data: 'player_segment' },
            { data: 'country' },
            { data: 'address' },
            { data: 'phone_number' },
            { data: 'email_verified',
             "render": function(data, type, row, meta){
                if(data == false){
                    data = 'No';
                }else{
                    data = 'Yes'
                }
                return data;
             }},
            { data: 'phone_verified',
            "render": function(data, type, row, meta){
                if(data == false){
                    data = 'No';
                }else{
                    data = 'Yes'
                }
                return data;
             }},
            { data: 'id_verified',
            "render": function(data, type, row, meta){
                if(data == false){
                    data = 'No';
                }else{
                    data = 'Yes'
                }
                return data;
             }},
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

        "language": {
            "info": " _START_ - _END_ of _TOTAL_",
            "infoEmpty": " 0 - 0 of 0",
            "infoFiltered": "",
            "paginate": {
                "next": "<button type='button' class='btn default' style='border:solid 1px #bdbdbd;'><i class='fas fa-caret-right'></button>",
                "previous": "<button type='button' class='btn default' style='border:solid 1px #bdbdbd;'><i class='fas fa-caret-left'></button>",
            },
            "lengthMenu": "_MENU_",
            searchPlaceholder: "  Enter user ID or username",
            search: "",
        },
    });

    $(function(){
        $("#min_date").datepicker();
        $("#max_date").datepicker();
    });

    $('#min_date, #max_date, #segmentation_filter').change(function () {
        vip_table.draw();
    });

});