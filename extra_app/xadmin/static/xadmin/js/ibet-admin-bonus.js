$(document).ready(function() {

    var bonus_table = $('#bonus_table').DataTable({
        "serverSide": true,
        "searching": true,
        "language": {
            "info": " _START_ - _END_ of _TOTAL_",
            "infoEmpty": " 0 - 0 of 0",
            "infoFiltered": "",
            "paginate": {
                "next": "<button type='button' class='btn default' style='border:solid 1px #bdbdbd;'><i class='fas fa-caret-right'></i></button>",
                "previous": "<button type='button' class='btn default' style='border:solid 1px #bdbdbd;'><i class='fas fa-caret-left'></i></button>"
            },
            "lengthMenu": "_MENU_",
            searchPlaceholder: "  Enter bonus or campaign name",
            search: "",
        },
        "columnDefs": [
            {
                orderable: false,
                targets: "no-sort"
            }
        ],
        "ajax": {
            type: 'GET',
            url: bonus_url,
            data: {
                'type': 'adminBonusList',
                'bonus_type': function() {var type=$('#bonus_type_filter :selected').val(); return type;},
                'bonus_status': function() {var status=$('#bonus_status_filter :selected').val(); return status;},
                'search': function () { return $('#bonus-search').val(); },
            },
        },
        columns: [
            { "data": 'name' },
            { "data": 'campaign' },
            { "data": 'type' },
            { "data": 'total_amount_issued' },
            { "data": 'total_count_issued' },
            { "data": 'total_amount_redeemed' },
            { "data": 'total_count_redeemed',},
            { "data": 'start_time',
                "render": function(data, type, row, meta){
                    data = formatDatetime(data)
                    return data;
                }
             },
            { "data": 'end_time',
                "render": function(data, type, row, meta){
                    data = formatDatetime(data)
                    return data;
                }
             },
            { "data": 'status' },
        ],
    });

    $('#bonus_status_filter, #bonus_type_filter').change(function () {
        bonus_table.draw();
    });

    $('#bonus-search-btn').click(function () {
        bonus_table.draw();
    });

    function formatDatetime(data){
        if(data === 'None'){
            data = '';
        }else{
            data = moment(data).format('MMM DD YYYY, HH:mm');
        }
        return data;
    }
});


