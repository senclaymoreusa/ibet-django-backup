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
                orderable: true,
                targets: "sort"
            }
        ],
        "ajax": {
            type: 'GET',
            data: {
                'type': 'getBonusList',
                'bonus_type': function() {var type=$('#bonus_type_filter :selected').val(); return type;},
                'bonus_status': function() {var status=$('#bonus_status_filter :selected').val(); return status;},
            },
        },
        columns: [
            { data: 'name' },
            { data: 'campaign' },
            { data: 'type' },
            { data: 'amount_issued' },
            { data: 'quantity_issued' },
            { data: 'amount_redeemed' },
            { data: 'quantity_redeemed' },
            { data: 'start_date' },
            { data: 'end_date' },
            { data: 'status' },
        ],
    });

    $('#bonus_status_filter, #bonus_type_filter').on('change', function () {
        bonus_table.draw();
    });
});
