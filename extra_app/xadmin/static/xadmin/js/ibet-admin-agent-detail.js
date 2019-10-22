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

    // DOWNLINE LIST TABLE
    var downlineListTable = $('#downline_list_table, #channel_report_table, #platform_winloss_table').DataTable({
        responsive: true,
        dom: 'B<ftilp>',
        buttons: [
            'csv'
        ],
        "columnDefs": [{
            "searchable": false, "targets": [0, 1],
        }],
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

    var affiliateCommissionTable = $('#affiliate-monthly-commission-table').DataTable({
        responsive: true,
        dom: 'B',
        buttons: [
            'csv'
        ],
        "columnDefs": [{
            "searchable": false, "targets": [0, 1],
        }],
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
    })
    $(".dt-buttons .dt-button.buttons-csv.buttons-html5").text("Export")

    // date range search
    $.fn.dataTable.ext.search.push(
        function (settings, data, dataIndex) {
            var min = $('#min').datepicker("getDate");
            var max = $('#max').datepicker("getDate");

            var dateParts = data[2].split("/");
            var newDate = dateParts[1] + '/' + dateParts[0] + '/' + dateParts[2]
            var startDate = new Date(newDate);

            if (min == null && max == null) { return true; }
            if (min == null && startDate <= max) { return true; }
            if (max == null && startDate >= min) { return true; }
            if (startDate <= max && startDate >= min) { return true; }
            return false;
        }
    );

    $("#min").datepicker({ onSelect: function () { downlineListTable.draw(); }, changeMonth: true, changeYear: true });
    $("#max").datepicker({ onSelect: function () { downlineListTable.draw(); }, changeMonth: true, changeYear: true });

    // Event listener to the two range filtering inputs to redraw on input
    $('#min, #max').change(function () {
        downlineListTable.draw();
    });

    // ACTIVITY
    $('#activity-type').change(function () {
        var activity = $('#activity-type').val();
        getActivityfilter(activity);
    });

    function getActivityfilter(activity) {
        var affiliate_id = $('#affiliate-id').val();
        $.ajax({
            type: 'POST',
            url: "{% url 'xadmin:agent_detail' %}",
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
            alert("Input cannout be empty");
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
                url: "{% url 'xadmin:agent_detail' %}",
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


    $(document).on("click", "#refer_link_remove", function () {
        var refer_link_id = $(this).parent().parent().find('#refer_link_id').val();
        var refer_row = $(this).closest('.row')
        $.ajax({
            type: 'POST',
            url: "{% url 'xadmin:agent_detail' %}",
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
            var new_commission_level = $('#commission_level_details').clone();
            $(new_commission_level).find('input').val('');
            var level = $('.commission_levels #commission_level_details').last().find('#commission_level_label').text();
            $(new_commission_level).find('#commission_level_label').text(+level + 1);
            $(new_commission_level).append(delete_btn);
            $('.commission_levels').append(new_commission_level)
        }
    });

    function checkCommissionLevelEmpty() {
        var $empty = $(".commission_levels input[required]").filter(function () {
            return !this.value.trim();
        }),
            valid = $empty.length == 0,
            items = $empty.map(function () {
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

    $(document).on("click", "#delete_commission_level_btn", function () {
        var current_level = $(this).parent().parent().find('#commission_level_label').html();
        if (current_level === '1') {
            $('#add_level_errorMessage').text("You can't delete level 1");
            $('#add_level_errorMessage').css('color', 'red');
        } else {
            var delete_btn = $('#delete_commission_level');
            var commission_id = $(this).parent().parent().find('#commission_id').val();
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
                level_detail['pk'] = $(this).find('#commission_id').val();
                level_detail['level'] = $(this).find('#commission_level_label').text();
                level_detail['rate'] = $(this).find('#commission_rate').val();
                level_detail['downline_rate'] = $(this).find('#downline_commission_rate').val();
                level_detail['active_downline'] = $(this).find('#active_downline').val();
                level_detail['downline_ftd'] = $(this).find('#downline_monthly_ftd').val();
                level_details.push(level_detail);
            });
            var affiliate_detail = [];
            affiliate_detail.push($('#affiliate-manager').val());
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
            var manager = $('#affiliate-manager').val()
            $.ajax({
                type: 'POST',
                url: "{% url 'xadmin:agent_detail' %}",
                data: {
                    'type': 'affiliate_audit',
                    'admin_user': admin_user,
                    'affiliate_detail[]': affiliate_detail,
                    'level_details': JSON.stringify(level_details),
                    'affiliate_id': affiliate_id,
                    'manager':manager
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
            url: "{% url 'xadmin:agent_detail' %}",
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

    $('#affiliate-manager').keyup(function () {
        var text = $('#affiliate-manager').val();
        $("#affiliate-manager").autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: "{% url 'xadmin:agent_detail' %}",
                    dataType: 'json',
                    type: 'GET',
                    data: {
                        'type': 'search_affiliate_manager',
                        'text': text
                    },
                    success: function (data) {
                        response(data);
                    }
                });
            },
            minLength: 1,
            //select
            select: function (e, ui) {
                // alert(ui.item.value);
            },
            open: function () {
                $(this).removeClass("ui-corner-all").addClass("ui-corner-top");
            },
            close: function () {
                $(this).removeClass("ui-corner-top").addClass("ui-corner-all");
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

});



