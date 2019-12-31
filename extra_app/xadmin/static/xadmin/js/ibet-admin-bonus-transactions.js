$(document).ready(function() {

    var csrftoken = $.cookie("csrftoken");

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

    var bonusTransactionsTable = $('#bonus-transactions-table').DataTable({
        "serverSide": true,
        "searching": true,
        "dom": '<<t>pil>',
        "language": {
            "info": " _START_ - _END_ of _TOTAL_",
            "infoEmpty": " 0 - 0 of 0",
            "infoFiltered": "",
            "paginate": {
                "next": "<button type='button' class='btn default' style='border:solid 1px #bdbdbd;'><i class='fas fa-caret-right'></i></button>",
                "previous": "<button type='button' class='btn default' style='border:solid 1px #bdbdbd;'><i class='fas fa-caret-left'></i></button>"
            },
            "lengthMenu": "_MENU_",
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
                'type': 'bonus_transactions_admin',
                'bonus_type': function() {var type=$('#bonus_type_filter :selected').val(); return type;},
                'ube_status': function() {var status=$('#bonus_status_filter :selected').val(); return status;},
                'search': function () { return $('#bonus-transactions-search').val(); },
                'min_date': function () { return $('#bonus-delivery-start').val(); },
                'max_date': function () { return $('#bonus-delivery-end').val(); },
            },
        },
        columns: [
            { "data": 'event.pk' },
            { "data": 'event.fields.owner',
                "render": function(data, type, row, meta){
                if(type === 'display'){
                    data = '<a href=' + user_link + data + '>' + data+ '</a>';
                }
                return data;
             }},
            { "data": 'username',
                "render": function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href=' + user_link + row['event']['fields']['owner'] + '>' + data + '</a>';
                    }
                    return data;
            }},
            { "data": 'bonus.fields.type' },
            { "data": 'bonus.fields.name' },
            { "data": 'event.fields.delivery_time',
//                "render": function(data, type, row, meta){
//                    data = formatDatetime(data)
//                    return data;
//                }
             },
            { "data": 'event.fields.completion_time',
//                "render": function(data, type, row, meta){
//                    data = formatDatetime(data)
//                    return data;
//                }
             },
            { "data": 'event.fields.amount' },
            { "data": 'event.fields.completion_percentage' },
            { "data": 'delivered_by_username',
                "render": function(data, type, row, meta){
                    if(type === 'display'){
                        data = '<a href=' + user_link + row['event']['fields']['delivered_by'] + '>' + data + '</a>';
                    }
                    return data;
            }},
            { "data": 'event.fields.status' },
            {
                "data": null,
                defaultContent:  "<button id='edit-ube-btn' class='btn btn-primary' type='button' data-toggle='modal' data-target='#edit-ube'><i class='fa fa-search'></i></button>"
            }
        ],
    });

    $("#bonus-delivery-start").datepicker();
    $("#bonus-delivery-end").datepicker();

    $('#bonus_status_filter, #bonus_type_filter').change(function(){
        bonusTransactionsTable.draw();
    });

    $('#bonus-search-btn, #bonus-delivery-btn').click(function(){
        bonusTransactionsTable.draw();
    });

    // export bonus records table
    var bonusTableHead = [];

    $('#export-bonus-transactions').click(function(){
        GetCellValues("bonus-transactions-table");
        bonusTableHead = JSON.stringify(bonusTableHead);
        document.location = bonus_url + '?export=' + true + '&tableHead=' + bonusTableHead;
    });

    function GetCellValues(tableId) {
        var table = document.getElementById(tableId);
        for (var i = 0, m = table.rows[0].cells.length - 1; i < m; i++) {
            bonusTableHead.push(table.rows[0].cells[i].innerHTML);
        }
    }


    // helper function
    function formatDatetime(data){
        if(data === 'None' || data === null){
            data = '';
        }else{
            data = moment(data).format('MMM DD YYYY, HH:mm');
        }
        return data;
    }
});