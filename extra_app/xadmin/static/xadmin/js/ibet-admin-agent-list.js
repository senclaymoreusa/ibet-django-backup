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

    var admin_user = $('#admin_user').val();
    // send data to commission pop-up window
    $('#commission tbody').on('click', 'button', function () {
        var data = commissionTable.row($(this).parents('tr')).data();
        showCommissionDetail(data);
        $.ajax({
            type: 'GET',
            url: agent_detail_url,
            data: {
                'type': 'getCommissionHistory',
                'date': data[0],
            },
            success: function (data) {
                addCommissionHistory(data);
                releaseCommission();
            },
        })
    })

    showCommissionDetail = function (data) {
        $("#period").empty();
        $("#period").append(data[0]);
        $("#valid-affiliate-count").empty();
        $("#valid-affiliate-count").append(data[1]);
        $("#total-commission").empty();
        $("#total-commission").append(data[3]);
    }

    addCommissionHistory = function (data) {
        $("#commission_statement").empty();
        content = "";
        for (var i = 0; i < data.length; i++) {
            content += '<tr id="commission_statement">';
            if (data[i].release_time.length === 0) {
                content += '<td id="commissionCheckbox"><input type="checkbox" name="commission_checkbox" /></td>';
            } else {
                content += '<td></td>'
            }
            content += '<td>' + data[i].id + '</td>';
            content += '<td>' + data[i].active_players + '</td>';
            content += '<td>' + data[i].downline_ftd + '</td>';
            content += '<td>' + data[i].commission_rate + '%' + '</td>';
            content += '<td>' + data[i].deposit + '</td>';
            content += '<td>' + data[i].withdrawal + '</td>';
            content += '<td>' + data[i].bonus + '</td>';
            content += '<td>' + data[i].winorloss + '</td>';
            content += '<td>' + data[i].commission + '</td>';
            content += '<td>' + data[i].status + '</td>';
            content += '<td>' + data[i].release_time + '</td>';
            content += '<td>' + data[i].operator + '</td>';
            content += '<td style="display: none" id="tran_pk">' + data[i].trans_pk + '</td>';
            content += '</tr>';
        }
        $("#commission_statement").append(content);

        var commission_detail_table = $('#commission_detail').DataTable({
            retrieve: true,
            responsive: true,
            dom: 'B<ftilp>',
            buttons: [
                'csv'
            ],
            "columnDefs": [{
                "searchable": false, "targets": [1],
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
        $(".dt-buttons .dt-button.buttons-csv.buttons-html5").text("Export")

    }

    releaseCommission = function () {
        var checkedlist = []
        var checkednumber = 0
        $('input[name="commission_checkbox"]').click(function () {
            var tranPK = $(this).closest('tr').find('#tran_pk').html();
            if ($(this).prop("checked") == true) {
                checkednumber += 1;
                checkedlist.push(tranPK);
            } else if ($(this).prop("checked") == false) {
                checkednumber -= 1;
                for (i = 0; i < checkedlist.length; i++) {
                    if (checkedlist[i] === tranPK) {
                        checkedlist.pop(checkedlist[i]);
                        break;
                    }
                }
            }
            if (checkednumber == 0) {
                $('#selected').empty();
            } else {
                $('#selected').text(checkednumber + ' selected');
            }
        });

        $('#commission-release-btn').click(function () {
            $.ajax({
                type: 'POST',
                url: agent_list_url,
                data: {
                    'type': 'releaseCommission',
                    'list[]': checkedlist,
                },
                success: function (data) {
                    window.location.reload();
                },
            })
        });
    }


    $('#affiliate_application tbody').on('click', 'button', function () {
        var data = $(this).closest('tr').find('#userID').html();
        $.ajax({
            type: 'GET',
            url: agent_detail_url,
            data: {
                'type': 'getAffiliateApplicationDetail',
                'user_id': data,
            },
            success: function (data) {
                addUserInfo(data);
            },
        })
    })
    addUserInfo = function (data) {
        $("#user-info-first-col").empty();
        content_col1 = "";
        content_col1 += '<li>' + data.id + '</li>';
        content_col1 += '<li>' + data.username + '</li>';
        content_col1 += '<li>' + data.first_name + '</li>';
        content_col1 += '<li>' + data.last_name + '</li>';
        content_col1 += '<li>' + data.birthday + '</li>';
        $("#user-info-first-col").append(content_col1);
        $("#user-info-second-col").empty();
        content_col2 = "";
        content_col2 += '<li>' + data.email + '</li>';
        content_col2 += '<li>' + data.phone + '</li>';
        content_col2 += '<li>' + data.address + '</li>';
        $("#user-info-second-col").append(content_col2);
        $("#user_intro").empty();
        $("#user_intro").append(data.intro);
        $("#affiliate_id").val(data.id);
    };

    $('#affiliate-application-approve-btn').click(function () {
        var remark = $('textarea#affiliate_application_remark').val();
        var userID = $(this).prev('input').val();

        $.ajax({
            type: 'POST',
            url: agent_detail_url,
            data: {
                'type': 'affiliateApplication',
                'result': "Yes",
                'remark': remark,
                'user_id': userID,
                'admin_user': admin_user,
            },
            success: function (data) {
                window.location.reload();
            },
        })
    });
    $('#affiliate-application-decline-btn').click(function () {
        var remark = $('textarea#affiliate_application_remark').val();
        var userID = $(this).prev().prev('input').val();

        $.ajax({
            type: 'POST',
            url: agent_detail_url,
            data: {
                'type': 'affiliateApplication',
                'result': "No",
                'remark': remark,
                'user_id': userID,
                'admin_user': admin_user,
            },
            success: function (data) {
                window.location.reload();
            },
        })
    });

    // datatable

    var affiliateTable = $('#affiliates').DataTable({
        responsive: true,
        dom: 'B<ftilp>',
        buttons: [
            'csv'
        ],
        "columnDefs": [{
            "searchable": false, "targets": [1],
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
    var commissionTable = $('#commission').DataTable({
        responsive: true,
        dom: 'B<ftilp>',
        buttons: [
            'csv'
        ],
        "columnDefs": [{
            "searchable": false,
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
    var premiumApplicationTable = $('#affiliate_application').DataTable({
        responsive: true,
        dom: 'B<ftilp>',
        buttons: [
            'csv'
        ],
        "columnDefs": [{
            "searchable": false,
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

    $('#search-btn').on('keyup click', function () {
        affiliateTable.search($('#search').val()).draw();
    });

    $(".dt-buttons .dt-button.buttons-csv.buttons-html5").text("Export")
})