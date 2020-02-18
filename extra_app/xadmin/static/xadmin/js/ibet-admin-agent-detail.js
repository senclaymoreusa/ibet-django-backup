
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

        var affiliate_id = $('#affiliate-id').val();
        var admin_user = $('#admin_user').val();

        $(function () {
            $('#min_date').datepicker({
                autoclose: true,
                todayHighlight: true,
                endDate: new Date()
            }).val('');
            $('#max_date').datepicker({
                autoclose: true,
                todayHighlight: true,
                endDate: new Date()
            }).val('');
        });

        // DOWNLINE LIST TABLE
        var downlineListTable = $('#downline-list-table').DataTable({
            "serverSide": true,
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
            dom: '<<t>Bpil>',
            "columnDefs": [
                {
                    "orderable": false,
                    "targets": 0
                }
            ],
            "ajax": {
                type: 'GET',
                url: agent_detail_url,
                data: {
                    'type': 'downlinePerformance',
                    'affiliateId': affiliate_id,
                    'accountType': function() {var type=$('#account_type_filter :selected').val(); return type;},
                    'channel': function() {var channel=$('#channel_filter :selected').val(); return channel;},
                    'minDate': function () { return $('#min_date').val(); },
                    'maxDate': function () { return $('#max_date').val(); },
                },
            },
            columns: [
                {data: 'player_id'},
                {data: 'registration_date', "render": function(data, type, row, meta){
                        return formatDatetime(data);
                }},
                {data: 'last_login', "render": function(data, type, row, meta){
                        return formatDatetime(data);
                }},
                {data: 'channel'},
                {data: 'ftd', "render": function(data, type, row, meta){
                        return formatDatetime(data);
                }},
                {data: 'total_deposit'},
                {data: 'total_withdrawal'},
                {data: 'total_bonus'},
                {data: 'total_adjustment'},
                {data: 'balance'},
                {data: 'turnover'},
            ],
        });

        $('#account_type_filter, #channel_filter, #min_date, #max_date').on('change', function () {
            downlineListTable.draw();
        });

        function formatDatetime(data){
            if(data === 'None'){
                data = '';
            }else{
                data = moment(data).format('MMM DD YYYY, HH:mm');
            }
            return data;
        }

        // AFFILIATE COMMISSION HISTORY EXPORT
        var commissionTableHead = [];
        $('#export-commission-history').on('click', function(){
            GetCellValues("affiliate-monthly-commission-table");
            commissionTableHead = JSON.stringify(commissionTableHead);
            document.location = document.location.href + '?tableHead=' + commissionTableHead;
        });

        function GetCellValues(tableId) {
            var table = document.getElementById(tableId);
            for (var i = 0, m = table.rows[0].cells.length; i < m; i++) {
                commissionTableHead.push(table.rows[0].cells[i].innerHTML);
            }
        }

        // ACTIVITY
        $('#activity-type').change(function () {
            var activity = $('#activity-type').val();
            getActivityfilter(activity);
        });

        function getActivityfilter(activity) {
            var affiliate_id = $('#affiliate-id').val();
            $.ajax({
                type: 'POST',
                url: agent_detail_url,
                data: {
                    'type': 'activity_filter',
                    'activity_type': activity,
                    'affiliate_id': affiliate_id,
                },
                success: function (data) {
                    displayActivity(data);
                }
            });
        }

        function displayActivity(data) {
            $("#select-filter").empty();
            content = "";
            for (var i = 0; i < data.length; i++) {
                content += '<div class="note-author">' + data[i].adminUser + '</div>';
                content += '<div class="note-block">' + data[i].message + '</div>';
            }
            $("#select-filter").append(content);
        }

        $('#post-btn').click(function (e) {
            e.preventDefault();
            var message = $('#notes-input').val();
            if (!message) {
                alert("Input cannot be empty");
            }else{
                updateNote(message);
            }
        });

        $('#adjustment_submit').click(function () {
            var adjustment_amount = $('#adjustment_amount_input').val()
            if (!adjustment_amount) {
                $('#errorMessage').text("Please fill the amount");
                $('#errorMessage').css('color', 'red');
            } else {
                var subject = $('#adjustment_message_subject').val()
                var text = $('#adjustment_message_text').val()
                var remark = $('#reason_for_adjustment_changes').html();
                var send = false;
                if ($('#adjustment_message_checkbox').prop("checked")) {
                    send = true;
                }
                $.ajax({
                    type: 'POST',
                    url: agent_detail_url,
                    data: {
                        'type': 'make_adjustment',
                        'admin_user': admin_user,
                        'remark': remark,
                        'amount': adjustment_amount,
                        'affiliate_id': affiliate_id,
                        'subject': subject,
                        'text': text,
                        'send': send,
                    },
                    success: function (data) {
                        location.reload();
                    }
                });
            }
        });

        $(document).on("click", ".refer_link_remove", function () {
            var refer_link_id = $(this).parent().parent().find('.refer_link_id').val();
            var refer_row = $(this).closest('.row')
            $.ajax({
                type: 'POST',
                url: agent_detail_url,
                data: {
                    'type': 'remove_refer_link',
                    'refer_link': refer_link_id,
                    'admin_user': admin_user,
                    'affiliate_id': affiliate_id,
                },
                success: function (data) {
                    refer_row.remove();
                }
            });
        });

        $(document).on("click", "#add_commission_level", function () {
            // check previous level has empty input or not
            if (checkCommissionLevelEmpty() == false) {
                var delete_btn = $('#delete_commission_level')
                delete_btn.remove();
                var commission_settting = $("input[name='commission-set']:checked").val();
                if (commission_settting === 'System') {
                    var new_commission_level = $('#system_commission_level_details').clone();
                    var level = $('.commission_levels #system_commission_level_details').last().find('.commission_level_label').text();
                } else {
                    var new_commission_level = $('#personal_commission_level_details').clone();
                    var level = $('.commission_levels #personal_commission_level_details').last().find('.commission_level_label').text();
                }
                $(new_commission_level).find('input').val('');

                $(new_commission_level).find('.commission_level_label').text(+level + 1);
                $(new_commission_level).append(delete_btn);
                $('.commission_levels').append(new_commission_level)
            }
        });

        function checkCommissionLevelEmpty() {
            var empty = $(".commission_levels input[required]").filter(function () {
                return !this.value.trim();
            }),
                valid = empty.length == 0,
                items = empty.map(function () {
                    return this.placeholder
                }).get();

            if (!valid) {
                // has empty
                $('#add_level_errorMessage').text("Please fill the empty input");
                $('#add_level_errorMessage').css('color', 'red');
                return true;
            } else {
                // no empty
                return false;
            }
        }

        $(document).on("click", '#copy-link', function(){
            var link = $('#promotion-link').text();
            copyToClipboard(link);
        });

        $(document).on("click", '.copy-link-list', function(){
            var link = $(this).parent().parent().find('.refer-link-list').text();
            copyToClipboard(link);
        });

        $(document).on("click", '#new-referral-save-btn', function(){
            var new_channel_name = $('#refer-channel-name').val();
            if (new_channel_name.length === 0) {
                $('#new-refer-channel-errorMessage').text("Please enter valid channel name!");
                $('#new-refer-channel-errorMessage').css('color', 'red');
            }else{
                $.ajax({
                    type: 'POST',
                    url: agent_detail_url,
                    data: {
                        'type': 'add_referral_channel',
                        'affiliate_id': affiliate_id,
                        'new_channel_name': new_channel_name,
                    },
                    success: function (data) {
                        addReferChannel(data);
                        $("#new-refer-channel").modal('toggle');
                    },
                    error: function(data){
                        $('#new-refer-channel-errorMessage').text(data.responseJSON.error);
                        $('#new-refer-channel-errorMessage').css('color', 'red');
                    }
                });
            }
        });

        function addReferChannel(data){
            data = $.parseJSON(data);
            var lastDiv = $('.refer_link_row').last().clone();
            lastDiv.find('.refer_link_id').val(data.pk)
            lastDiv.find('.refer-link-name').text(data.name)
            lastDiv.find('.refer-link-list').text(data.link)
            lastDiv.find('.refer-link-date').text(moment(new Date(data.time)).format('MMM DD YYYY, HH:mm'))
            $('.promotion-links').append(lastDiv);
        }

        $(document).on("click", "#delete_commission_level_btn", function () {
            var current_level = $(this).parent().parent().find('.commission_level_label').html();
            if (current_level === '1') {
                $('#add_level_errorMessage').text("You can't delete level 1");
                $('#add_level_errorMessage').css('color', 'red');
            } else {
                var delete_btn = $('#delete_commission_level');
                var commission_id = $(this).parent().parent().find('.commission_id').val();
                var commission_row = $(this).prev().closest('.row');
                var commission_row_prev = commission_row.prev('.row')
                commission_row.remove();
                commission_row_prev.append(delete_btn);
            }
        });

        $(document).on("click", "#affiliate_audit_save_btn", function () {
            if (checkCommissionLevelEmpty() == false) {
                level_details = [];
                $(".commission_levels .row").each(function () {
                    level_detail = {};
                    level_detail['pk'] = $(this).find('.commission_id').val();
                    level_detail['level'] = $(this).find('.commission_level_label').text();
                    level_detail['rate'] = $(this).find('.commission_rate').val();
                    level_detail['downline_rate'] = $(this).find('.downline_commission_rate').val();
                    level_detail['active_downline'] = $(this).find('.active_downline').val();
                    level_detail['downline_ftd'] = $(this).find('.downline_monthly_ftd').val();
                    level_detail['downline_ngr'] = $(this).find('.downline_net_profit').val();
                    level_details.push(level_detail);
                });
                var manager = $('#manager_assign_chosen a span').html()
                var affiliate_detail = [];
                affiliate_detail.push(manager);
                if ($('#affiliate-level-normal').is(':checked')) {
                    affiliate_detail.push("Normal");
                } else {
                    affiliate_detail.push("VIP");
                }
                if ($('#affiliate-status-normal').is(':checked')) {
                    affiliate_detail.push("Enable");
                } else {
                    affiliate_detail.push("Disabled");
                }
                if ($('#commission-set-system').is(':checked')) {
                    affiliate_detail.push("System");
                } else {
                    affiliate_detail.push("Personal");
                }
                if ($('#commission-transfer-system').is(':checked')) {
                    affiliate_detail.push("Yes");
                } else {
                    affiliate_detail.push("No");
                }

                $.ajax({
                    type: 'POST',
                    url: agent_detail_url,
                    data: {
                        'type': 'affiliate_audit',
                        'admin_user': admin_user,
                        'affiliate_detail[]': affiliate_detail,
                        'level_details': JSON.stringify(level_details),
                        'affiliate_id': affiliate_id,
                        'manager': manager,
                    },
                    success: function (data) {
                        location.reload();
                    }
                });
            }
        });

        function updateNote(message) {
            var affiliate_id = $('#affiliate-id').val();
            $.ajax({
                type: 'POST',
                url: agent_detail_url,
                data: {
                    'type': 'update_message',
                    'affiliate_id': affiliate_id,
                    'admin_user': admin_user,
                    'message': message,
                },
                success: function (data) {
                    location.reload();
                }
            });
        }

        $('.manager-assign').chosen({ width: "70%" });

        $('#edit-details-btn').on('click', function(){
            var commission_settting = $("input[name='commission-set']:checked").val();
            if (commission_settting === 'System') {
                $('#system_commission_levels').css('display', '');
            } else {
                $('#personal_commission_levels').css('display', '');
            }
        });

        $("input[name='commission-set']").on('change', function(){
            var val = $("input[name='commission-set']:checked").val();
            if (val === 'System') {
                $('#system_commission_levels').css('display', '');
                $('#personal_commission_levels').css('display', 'none');
            } else {
                $('#system_commission_levels').css('display', 'none');
                $('#personal_commission_levels').css('display', '');

            }
        });

    });

    function copyToClipboard(value) {
        var aux = document.createElement("input");
        aux.setAttribute("value", value);
        document.body.appendChild(aux);
        aux.select();
        document.execCommand("copy");
        document.body.removeChild(aux);
    }





