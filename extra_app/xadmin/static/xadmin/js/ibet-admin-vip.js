$(document).ready(function () {

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

    var exportReq = "No";
    var vipTableHead = [];

    var vip_table = $('#vip_table').DataTable({
        "serverSide": true,
        "searching": true,
        "ordering": false,
        "dom": '<<t>pil>',
        "ajax": {
            type: 'GET',
            url: vip_url,
            data: {
                'type': 'getVIPInfo',
                'system': 'vip_admin',
                'segment': function() {var segment=$('#segmentation_filter :selected').val(); return segment;},
                'minDate': function () { return $('#min_date').val(); },
                'maxDate': function () { return $('#max_date').val(); },
                'search': function () { return $('#vip-search').val(); },
                'export': function () { return exportReq; },
            },
        },

        "columns": [
            { data: 'player_id',
              "render": function(data, type, row, meta){
                if(type === 'display'){
                    data = '<a id="user-id" href=' + user_link + data + '>' + data+ '</a>';
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
            {
                data: null,
                defaultContent:  "<button id='edit-vip-btn' class='btn btn-primary' type='button' data-toggle='modal' data-target='#edit-vip'><i class='fa fa-search'></i></button>"
            }
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

    $('#export-vip').click(function(){
        exportReq = "Yes";
        GetCellValues("vip_table");
        vipTableHead = JSON.stringify(vipTableHead);
        document.location = vip_export + '?tableHead=' + vipTableHead;
    });

    function GetCellValues(tableId) {
        var table = document.getElementById(tableId);
        for (var i = 0, m = table.rows[0].cells.length - 1; i < m; i++) {
            vipTableHead.push(table.rows[0].cells[i].innerHTML);
        }
    }

    $('#min_date, #max_date, #segmentation_filter').change(function () {
        vip_table.draw();
    });

    $('#vip-search-btn').click(function () {
        vip_table.draw();
    });

    $('#vip_table tbody').on('click', 'button', function () {
        var userId = $(this).closest('tr').find('#user-id').html();
        $.ajax({
            type: 'GET',
            url: vip_url,
            data: {
                'type': 'getVIPDetailInfo',
                'userId': userId,
            },
            success: function (data) {
                addVIPUserInfo(data);
            },
        })
    })

    addVIPUserInfo = function (data) {
        // DISPLAY VIP DETAIL INFO
        $("#vip-player-info").empty();
        content = "";
        content += "<input type='hidden' id='vip-pk' value=" + data.pk + ">";
        content += data.username + '<br>';
        content += data.segment + '<br>';
        content += data.manager + '<br>';
        content += data.name + '<br>';
        content += data.id_number + '<br>';
        if (data.email_verified == false){
            content += data.email + "&nbsp;&nbsp;&nbsp;" + '<i class="fa fa-check-circle-o verified-invalid"></i>' + '<br>';
        }else{
            content += data.email + "&nbsp;&nbsp;&nbsp;" + '<i class="fa fa-check-circle-o verified-valid"></i>' + '<br>';
        }
        if (data.phone_verified == false){
            content += data.phone + "&nbsp;&nbsp;&nbsp;" + '<i class="fa fa-check-circle-o verified-invalid"></i>' + '<br>';
        }else{
            content += data.phone + "&nbsp;&nbsp;&nbsp;" + '<i class="fa fa-check-circle-o verified-valid"></i>' + '<br>';
        }
        content += data.birthday + '<br>';
        content += data.preferred_product + '<br>';
        content += data.preferred_contact + '<br>';
        $("#vip-player-info").append(content);
        if (data.segment == ''){
            $('#segmentation-assign').append("<option value='' selected disabled style='display:None'>Select segment</option>")
        }else{
            $('#segmentation-assign').append("<option value='' selected disabled style='display:None'>" + data.segment + "</option>")
        }

        if (data.manager == ''){
            console.log("empty")
            $('#manager-assign-default').val("Select manager")
            $('#manager-assign-default').text("Select manager")
        }else{
            console.log(data.manager)
            $('#manager-assign-default').val(data.manager)
            $('#manager-assign-default').text(data.manager)
        }
        $('.manager-assign').chosen({ width: "70%" });

    };



    $('#vip-details-save').click(function () {
        var segment = $('#segmentation-assign :selected').val();
        var manager = $('#manager_assign_chosen a span').html();
        var changeReason = $('#vip-change-reason').val();
        var userId = $('#vip-pk').val();

        $.ajax({
            type: 'POST',
            url: vip_url,
            data: {
                'type': 'editVIPDetail',
                'userId': userId,
                'segment': segment,
                'manager': manager,
                'changeReason': changeReason,
                'admin_user': admin_user,
            },
            success: function (data) {
                window.location.reload();
            },
        })
    });


});