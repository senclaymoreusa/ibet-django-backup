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

    var bonus_table = $('#bonus_table').DataTable({
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
            { "data": 'type' },
            { "data": 'total_amount_issued' },
            { "data": 'total_count_issued' },
            { "data": 'total_amount_redeemed' },
            { "data": 'total_count_redeemed',},
            { "data": 'start_time',
//                "render": function(data, type, row, meta){
//                    data = formatDatetime(data)
//                    return data;
//                }
             },
            { "data": 'end_time',
//                "render": function(data, type, row, meta){
//                    data = formatDatetime(data)
//                    return data;
//                }
             },
            { "data": 'status' },
        ],
    });

    $('#bonus_status_filter, #bonus_type_filter').change(function(){
        bonus_table.draw();
    });

    $('#bonus-search-btn').click(function(){
        bonus_table.draw();
    });

    // export bonus records table
    var bonusTableHead = [];

    $('#export-bonus-records').click(function(){
        GetCellValues("bonus_table");
        bonusTableHead = JSON.stringify(bonusTableHead);
        document.location = bonus_url + '?export=' + true + '&tableHead=' + bonusTableHead;
    });

    function GetCellValues(tableId) {
        var table = document.getElementById(tableId);
        for (var i = 0, m = table.rows[0].cells.length - 1; i < m; i++) {
            bonusTableHead.push(table.rows[0].cells[i].innerHTML);
        }
    }

    var productList = ["casino", "live-casino", "sports", "lottery"]

    var dataTarget;
    var providerChosen;

    // deposit bonus
    var bonusPer;           //bonus amount percentage
    var minDeposit;;        //add req for deposit
    var maxBonusAmount;     //total amounts per bonus can be released
    var depositWagerCal;    // Deposit + bonus(0) or Bonus only(1)

    // bonus 01
    var bonusStartTime;
    var bonusEndTime;

    //bonus 02
    var masterType = [];
    var bonusCategory;
    var issued = false;

    //manual bonus
    //bonus 03
    var bonusAmount;
    var wagerMasterValue = 0;
    var wagerList = [];     //admin
    var timeLimit = -1;     //admin
    var bonusAmountList = [];


    //bonus 05
    var targetAll;
    var targetAudience;
    var wagerRequirements;
    var excludedGroups;

    // triggered bonus
    var triggerType;        //verification,     deposit,        turnover
    var triggerSubType;     //id,email,phone    first, next     product, provider

    //bonus detail 06: bonus claim control
    var maxDailyTimes;
    var maxTotalTimes;
    var maxAssociatedAccounts;  //????
    var maxUser;
    var maxUserAmount;
    var maxTargetUserAmount;

    //bonus 07
    var deliveryMethod;

    // bonus 01
    $("#bonus-start-time").datepicker();
    $("#bonus-end-time").datepicker();

    $("#bonus-trigger-type input:checkbox").on('click', function() {
      var $box = $(this);
      if ($box.is(":checked")) {
        var group = "input:checkbox[name='" + $box.attr("name") + "']";
        $(group).prop("checked", false);
        $box.prop("checked", true);
        $('#bonus-trigger-type input:radio').prop("checked", false);
      } else {
        $box.prop("checked", false);
      }
    });

    $('.previous').on('click', function(){
        $('.modal').modal('hide');
    });

    // bonus 02
    $("input[name='bonus-category']").on('change', function(){
        bonusCategory = $(this).val();
        if(bonusCategory === "triggered"){
            $('#bonus-next-02').attr('data-target', '#bonus-03');
            $('#bonus-prev-04').attr('data-target', '#bonus-03');
        }else{
            $('#bonus-next-02').attr('data-target', '#bonus-04');
            $('#bonus-amount-detail').css('display', '');
            $('#bonus-prev-04').attr('data-target', '#bonus-02');
        }
    });

    // bonus 03
    $('#verification-bonus').on('change', function(){
        if($(this).is(":checked")){
            $('#verification-choices').show();
            $('#deposit-choices').hide();
            $('#turnover-choices').hide();
        }else{
            $('#verification-choices').hide();
        }
    });

    $('#deposit-bonus').on('change', function(){
        if($(this).is(":checked")){
            $('#deposit-choices').show();
            $('#verification-choices').hide();
            $('#turnover-choices').hide();
        }else{
            $('#deposit-choices').hide();
        }
    });

    $('#turnover-bonus').on('change', function(){
        if($(this).is(":checked")){
            $('#turnover-choices').show();
            $('#deposit-choices').hide();
            $('#verification-choices').hide();
        }else{
            $('#turnover-choices').hide();
        }
    });

    $('#product-selector').on('change', function(){
        $('#turnover-choices-product').prop('checked', true);
    });

    $('#provider-selector').chosen({width: "242px"}).change(function(){
        $('#turnover-choices-provider').prop('checked', true);
        providerChosen = $(this).chosen().val();
    });

    // bonus 04
    $('#bonus-amount').on('change', function(){
        bonusAmount = parseFloat($(this).val()).toFixed(2);
        $(this).prop('value', bonusAmount);
        bonusAmountList = [];
        bonusAmountList.push({
            "amount_type": "same",
            "bonus_amount": bonusAmount,
        });
    });

    $('#wager-casino-times').on('change', function(){
        wagerChange(this, "casino");
    });

    $('#wager-live-casino-times').on('change', function(){
        wagerChange(this, "live-casino");
    });

    $('#wager-sports-times').on('change', function(){
        wagerChange(this, "sports");
    });

    $('#wager-lottery-times').on('change', function(){
        wagerChange(this, "lottery");
    });

    $('#wager-casino').on('change', function(){
        wagerSelect(this, "casino");
    });
    $('#wager-live-casino').on('change', function(){
        wagerSelect(this, "live-casino");
    });
    $('#wager-sports').on('change', function(){
        wagerSelect(this, "sports");
    });
    $('#wager-lottery').on('change', function(){
        wagerSelect(this, "lottery");
    });


    $("#all-product").on('change', function () {
       if($("#all-product").is(':checked')){
            $.each($(".wager-product"), function(){
                $(".wager-product").prop("checked", "checked");
            })
        }else{
            $.each($(".wager-product"), function(){
                if($(this).is(':disabled')){
                    return;
                }else{
                    $(this).prop("checked", "");
                }
            })
        }
        for(var i = 0; i < productList.length; i++){
            var curProduct = productList[i];
            wagerSelect(document.getElementById("wager-" + curProduct), curProduct);
        }
    });


    //bonus 04-02
    //deposit bonus
    $("input[name='bonus-amount-type-deposit-choice']").on('change', function(){
        var amountType = $(this).val();
        $('#deposit-fixed style').detach();
        $('#deposit-percentage style').detach();
        $('#deposit-tiered style').detach();
        if(amountType === "percentage"){
            $('#wager-product-reqs').css("display", "");
            $('#deposit-percentage').css("display", "");
            $('#deposit-percentage').append('<style>.up-arrow:before{left:125px;}</style>');
            $('#deposit-percentage').append('<style>.up-arrow:after{left:126px;}</style>');
            $('#deposit-fixed').css("display", "none");
            $('#deposit-tiered').css("display", "none");
        }else if(amountType === "fixed"){
            $('#wager-product-reqs').css("display", "");
            $('#deposit-percentage').css("display", "none");
            $('#deposit-tiered').css("display", "none");
            $('#deposit-fixed').append('<style>.up-arrow:before{left:306px;}</style>');
            $('#deposit-fixed').append('<style>.up-arrow:after{left:307px;}</style>');
            $('#deposit-fixed').css("display", "");
        }else if(amountType === "tiered"){
            $('#wager-product-reqs').css("display", "none");
            $('#deposit-percentage').css("display", "none");
            $('#deposit-fixed').css("display", "none");
            $('#deposit-tiered').append('<style>.up-arrow:before{left:445px;}</style>');
            $('#deposit-tiered').append('<style>.up-arrow:after{left:446px;}</style>');
            $('#deposit-tiered').css("display", "");
        }
    });

    $("#bonus-amount-detail-02 input").on('change', function(){
        bonusAmountList = [];
        var amountType = $("input[name='bonus-amount-type-deposit-choice']:checked").val();
        if(amountType == "percentage"){
            minDeposit = $('#dp-min').val();
            bonusPer = $('#dp-percentage').val();
            maxBonusAmount = $('#dp-max-amount').val();
            bonusAmountList.push({
                "amount_type": amountType,
                "amount_threshold": minDeposit,
                "bonus_percentage": bonusPer,
                "max_bonus_amount": maxBonusAmount,
            });
        }else if(amountType == "fixed"){
            minDeposit = $('#df-min').val();
            bonusAmount = $('#df-bonus-amount').val();
            bonusAmountList.push({
                "amount_type": amountType,
                "amount_threshold": minDeposit,
                "bonus_amount": bonusAmount,
            });
        }else if(amountType == "tiered"){
            bonusAmountList.push({
                "amount_type": amountType,
            });
        }
    });

    //turnover bonus
    $("input[name='bonus-amount-type-turnover-choice']").on('change', function(){
        var amountType = $(this).val();
        $('#turnover-fixed style').detach();
        $('#turnover-percentage style').detach();
        $('#turnover-tiered style').detach();
        if(amountType === "percentage"){
            $('#wager-product-reqs').css("display", "");
            $('#turnover-percentage').css("display", "");
            $('#turnover-percentage').append('<style>.up-arrow:before{left:125px;}</style>');
            $('#turnover-percentage').append('<style>.up-arrow:after{left:126px;}</style>');
            $('#turnover-fixed').css("display", "none");
            $('#turnover-tiered').css("display", "none");
        }else if(amountType === "fixed"){
            $('#wager-product-reqs').css("display", "");
            $('#turnover-percentage').css("display", "none");
            $('#turnover-tiered').css("display", "none");
            $('#turnover-fixed').append('<style>.up-arrow:before{left:306px;}</style>');
            $('#turnover-fixed').append('<style>.up-arrow:after{left:307px;}</style>');
            $('#turnover-fixed').css("display", "");
        }else if(amountType === "tiered"){
//            $('#wager-product-reqs').css("display", "none")
            $('#turnover-percentage').css("display", "none");
            $('#turnover-fixed').css("display", "none");
            $('#turnover-tiered').append('<style>.up-arrow:before{left:445px;}</style>');
            $('#turnover-tiered').append('<style>.up-arrow:after{left:446px;}</style>');
            $('#turnover-tiered').css("display", "");
        }
    });

    $("#bonus-amount-detail-03 input").on('change', function(){
        bonusAmountList = [];
        var amountType = $("input[name='bonus-amount-type-turnover-choice']:checked").val();
        if(amountType == "percentage"){
            minDeposit = $('#tp-min').val();
            bonusPer = $('#tp-percentage').val();
            maxBonusAmount = $('#tp-max-amount').val();
            bonusAmountList.push({
                "amount_type": amountType,
                "amount_threshold": minDeposit,
                "bonus_percentage": bonusPer,
                "max_bonus_amount": maxBonusAmount,
            });
        }else if(amountType == "fixed"){
            minDeposit = $('#tf-min').val();
            bonusAmount = $('#tf-bonus-amount').val();
            bonusAmountList.push({
                "amount_type": amountType,
                "amount_threshold": minDeposit,
            });
        }else if(amountType == "tiered"){
            bonusAmountList.push({
                "amount_type": amountType,
            });
        }
    });

    function wagerSelect(element, product){
        if(element.checked){
            $('#' + product + '-unselected').css("display", "none");
            $('#' + product + '-selected').css("display", "");
            $('#wager-' + product + '-times').prop("required", true);
        }else{
            $('#' + product + '-unselected').css("display", "");
            $('#' + product + '-selected').css("display", "none");
            $('#wager-' + product + '-times').prop("required", false);
        }
    };

    function wagerChange(element, name){
        var wagerValue = $(element).val();
        $('#wager-' + name + '-total').attr('value', "");
        var curDepositAmountType = $("input[name='bonus-amount-type-deposit-choice']:checked").val();
        //for deposit bonus
        if(curDepositAmountType == "percentage" || triggerType === "turnover"){
            var hasMasterSingle = masterType.includes("casino") || masterType.includes("live-casino")
            || masterType.includes("sports");
            if(masterType.includes(name) || !hasMasterSingle){
                wagerMasterValue = wagerValue;
                $('#wager-' + name + '-total').attr('value', '    X');
                $('#wager-' + name + '-total').css('width', '40px');
            }else{
                if(wagerMasterValue > 0){
                    var str = " % = " +  Math.ceil(wagerMasterValue / wagerValue * 100) + "X";
                    $('#wager-' + name + '-total').attr('value', str);
                }
            }
        }else if($.isNumeric(wagerValue) && $.isNumeric(bonusAmount)){
            var hasMasterSingle = masterType.includes("casino") || masterType.includes("live-casino")
            || masterType.includes("sports");
            if(masterType.includes(name) || !hasMasterSingle){
                var str = " X " + bonusAmount + " = " + wagerValue * bonusAmount;
                wagerMasterValue = wagerValue;
                $('#wager-' + name + '-total').attr('value', str);
                $('#wager-' + name + '-total').css('width', '96px');
            }else{
                if(wagerMasterValue > 0){
                    var str = " % = " +  Math.ceil(wagerMasterValue / wagerValue * 100) + "X";
                    $('#wager-' + name + '-total').attr('value', str);
                }
            }
        }
    };


    // bonus 05
    $('#group-assigned').chosen({width: "242px"}).change(function(){
        $('#specific-accounts').prop('checked', true);
        targetAudience = $(this).chosen().val();
    });

    $('#bonus-requirements').chosen({width: "242px"}).change(function(){
        wagerRequirements = $(this).chosen().val();
    });

    $('#group-unassigned').chosen({width: "242px"}).change(function(){
        excludedGroups = $(this).chosen().val();
    });

    // helper function
    function formatDatetime(data){
        if(data === 'None'){
            data = '';
        }else{
            data = moment(data).format('MMM DD YYYY, HH:mm');
        }
        return data;
    }

    function checkEmpty(cur){
        curList = cur.id.split('-')
        var currentDivId = curList[0] + '-' + curList[2];
        var emptyLen = $('#' + currentDivId + " input:required").filter(function() {
            return this.value === "";
        });
        if(emptyLen.length > 0){
            showErrorMsg(cur);
            return false;
        }else{
            removeErrorMsg(cur);
        }
        return true;
    };

    function showErrorMsg(element){
        $('.errorMessage').show();
        $('.errorMessage').text("Please fill out the empty input.");
        $('.errorMessage').css('color', 'red');
        $(element).removeAttr('data-target');
    };

    function removeErrorMsg(element){
        $('.errorMessage').hide();
        $(element).attr('data-target', dataTarget);
        $('.modal').modal('hide');
    };

    function updateDataTarget(element){
        var target = $(element).attr('data-target');
        if(typeof target !== typeof undefined && target !== false) {
            dataTarget = $(element).attr('data-target');
        }
    }

     // new bonus
    $('#bonus-next-01').on('click', function(){
        updateDataTarget(this);
        bonusName = $('#bonus-name').val();
        bonusStartTime = $('#bonus-start-time').val();
        bonusEndTime = $('#bonus-end-time').val();
        checkEmpty(this);
    });

    $('#bonus-next-02').on('click', function(){
        updateDataTarget(this);
        $.each($("input[name='master-type']:checked"), function(){
            var curMasterType = $(this).val();
            masterType.push(curMasterType);
            if (curMasterType == "casino"){
                $('#wager-casino').prop('checked', true);
                $('#wager-casino').prop('disabled', true);
                $('#wager-casino-times').prop('required', true);
                $('#casino-unselected').css("display", "none");
                $('#casino-selected').css("display", "");
            }else if (curMasterType == "live-casino"){
                $('#wager-live-casino').prop('checked', true);
                $('#wager-live-casino').prop('disabled', true);
                $('#wager-live-casino-times').prop('required', true);
                $('#live-casino-unselected').css("display", "none");
                $('#live-casino-selected').css("display", "");
            }else if (curMasterType == "sports"){
                $('#wager-sports').prop('checked', true);
                $('#wager-sports').prop('disabled', true);
                $('#wager-sports-times').prop('required', true);
                $('#sports-unselected').css("display", "none");
                $('#sports-selected').css("display", "");
            }
        });
        if($('#bonus-issue').is(":checked")){
            issued = true;
        }else{
            issued = false;
        }
        if(!$("input:radio[name='bonus-category']").is(":checked") ||
        !$("input:checkbox[name='master-type']").is(":checked")){
            showErrorMsg(this);
        }else{
            removeErrorMsg(this);
        }
    });

    $('#bonus-next-03').on('click', function(){
        updateDataTarget(this);
        triggerType = $("input[name='bonus-trigger-type']:checked").val();
        if(triggerType === "verification"){
            triggerSubType = $("input[name='verification-choice']:checked").val();
            $('#bonus-amount-detail, .wager-req-01').css("display", "");
            $('#bonus-amount-detail-02, .wager-req-02').css("display", "none");
            $('#bonus-amount-detail-03').css("display", "none");
        }else if(triggerType === "deposit"){
            triggerSubType = $("input[name='deposit-choice']:checked").val();
            $('#bonus-amount-detail, .wager-req-01').css("display", "none");
            $('#bonus-amount-detail-02, .wager-req-02').css("display", "");
            $('#bonus-amount-detail-03').css("display", "none");
            if(triggerSubType === "next"){
                $('#deposit-tiered-col').hide();
            }else{
                $('#deposit-tiered-col').show();
            }
        }else if(triggerType === "turnover"){
            var turnoverChoice = $("input[name='turnover-choice']:checked").val();
            if(turnoverChoice === "product"){
                triggerSubType = $("#product-selector").val();
            }else if(turnoverChoice === "provider"){
                triggerSubType = providerChosen;
            }
            $('#bonus-amount-detail').css("display", "none");
            $('#bonus-amount-detail-02, .wager-req-02').css("display", "none");
            $('#bonus-amount-detail-03, .wager-req-01').css("display", "");
        }

        if(typeof triggerType === typeof undefined || typeof triggerSubType === typeof undefined || triggerSubType === null) {
            showErrorMsg(this);
        }else{
            removeErrorMsg(this, $(this).attr('data-target'));
        }

    });

    $('#bonus-next-04').on('click', function(){
        updateDataTarget(this);

        wagerList = [];
        timeLimit = $('#time-period').val();
         // manual deposit or verification bonus
        var emptyWager = $('#wager-reqs input:required').filter(function() {
            return this.value === "";
        });

        if(bonusCategory == "manual" || triggerType == "verification"){
            if($('#bonus-amount').value === "" || emptyWager.length > 0){
                showErrorMsg(this);
            }else{
                removeErrorMsg(this);
            }
        }else {
            //bonusAmountList should not be empty
            //depositWagerCal should not be empty
            var depositEmpty = false;
            var turnoverEmpty = false;
            var emptyAmount = $('#' + triggerType + '-' + bonusAmountList['amount_type'] + ' input:required').filter(function() {
                return this.value === "";
            });
            depositWagerCal = $("input[name='wager-cal']:checked").val();

            if(triggerType == "deposit"){
                if(emptyAmount.length > 0 || depositWagerCal === undefined){                      //deposit tiered bonus check
                    showErrorMsg(this);
                    depositEmpty = true;
                }

                if(bonusAmountList[0]['amount_type'] !== "tiered" && emptyWager.length > 0){   //deposit percentage,fixed bonus check
                    showErrorMsg(this);
                    depositEmpty = true;
                }

                if(depositEmpty === false ){
                    removeErrorMsg(this);
                    if(bonusAmountList[0]['amount_type'] === "tiered"){
                        bonusAmountList = [];
                        wagerList = [];
                        // for deposit tiered amount
                        $.each($('.deposit-tiered-amount'), function(){
                            bonusAmountList.push({
                                "amount_type": "tiered",
                                "amount_threshold": $(this).find('.dt-min').val(),
                                "bonus_percentage": $(this).find('.dt-percentage').val(),
                                "max_bonus_amount": $(this).find('.dt-max-amount').val(),
                            });
                            wagerList.push({
                                "casino": $(this).find('.dt-casino').val(),
                                "live-casino": $(this).find('.dt-live-casino').val(),
                                "sports": $(this).find('.dt-sports').val(),
                                "lottery": $(this).find('.dt-lottery').val(),
                            })
                        })
                    }
                }
            }else if(triggerType == "turnover"){
                //deposit bonus check
                if(emptyAmount.length > 0 || emptyWager.length > 0){
                    showErrorMsg(this);
                    turnoverEmpty = true;
                }
                if(turnoverEmpty === false ){
                    removeErrorMsg(this);
                    if(bonusAmountList[0]['amount_type'] === "tiered"){
                        bonusAmountList = [];
                        wagerList = [];// for deposit tiered amount
                        $.each($('.turnover-tiered-amount'), function(){
                            bonusAmountList.push({
                                "amount_type": "tiered",
                                "amount_threshold": $(this).find('.tt-min').val(),
                                "bonus_percentage": $(this).find('.tt-percentage').val(),
                            });
                        });
                    }
                }
            }
        }
        if (wagerList.length === 0){
            addWagerReq();
        }
    });

    function addWagerReq(){
        var tempDict = {}
        for(var i = 0; i < productList.length; i++){
            var curBox = $('#wager-' + productList[i]);
            if(curBox.is(':checked')){
                if(curBox.is(':disabled')){
                  tempDict[productList[i]] = $('#wager-' + productList[i] + '-times').val();
                }else{
                    var subWager = $('#wager-' + productList[i] + '-total').val().split(' ');
                    tempDict[productList[i]] = subWager[3].substring(0, subWager[3].length - 1);
                }
            }else{
                tempDict[productList[i]] = "-1";
            }
        }
        wagerList.push(tempDict);
    }

    $('#bonus-next-05').on('click', function(){
        updateDataTarget(this);
        // check empty, either openAll or selectGroup should be true, selectMustHave must be true
        if ($('#open-to-all').is(':checked')){
            targetAll = true;
            targetAudience = null;
        }else{
            targetAll = false
        }
        var selectGroup = $('#specific-accounts').is(':checked') && $('#group-assigned').val() !== null;
//        var selectMustHave = $('#bonus-requirements').val() !== null;
        if((!targetAll && !selectGroup)){
            showErrorMsg(this);
        }else{
            removeErrorMsg(this);
        }

    });

    $('#bonus-next-06').on('click', function(){
        updateDataTarget(this);
        if(checkEmpty(this) == true){
            maxDailyTimes = $('#daily-claim').val();
            maxTotalTimes = $('#total-claim').val();
            maxAssociatedAccounts = $('#associated-total-claim').val();
            maxUser = $('#maximum-claimer').val();
//            maxUserAmount = $('#max-user-amount').val();
            maxTargetUserAmount = $('#max-target-user-amount').val();
//            if(maxUserAmount.length === 0){
//                maxUserAmount = null
//            }
            if(maxTargetUserAmount.length === 0){
                maxTargetUserAmount = null
            }
        }
    });

    $('#publish').on('click', function () {
        $('#publish').html('Click to Publish');
        $('#publish').attr('id', 'publish-confirm');
        $('#publish-confirm').on('click', function(){
            var reqDict = {
                "wager_multiple": wagerList,
                "time_limit": timeLimit,
                "must_have": wagerRequirements,
                "aggregate_method": 0 //sum
            }

            var playersDict = {
                "target_all": targetAll,
                "target_player": targetAudience,
                "excluded_player": excludedGroups,
            }

            var bonusDict = {
                // bonus
                "name": bonusName,
                "start_time": bonusStartTime,
                "end_time": bonusEndTime,
                "issued": issued,
                "amount": bonusAmount,
                "percentage": bonusPer,
                "max_daily_times": maxDailyTimes,
                "max_total_times": maxTotalTimes,
                "max_associated_accounts": maxAssociatedAccounts,
                "max_user": maxUser,
//                "max_user_amount": maxUserAmount,
                "max_target_user_amount": maxTargetUserAmount,
                "delivery_method": $("input[name='delivery']").val(),
                "status": 1,                    // create -> active
                "players": playersDict,         // players
                "requirements": reqDict,        // requirements

                //new
                "type" :bonusCategory,              // manual or triggered
                "trigger_type": triggerType,        // verification,     deposit    or   turnover
                "trigger_subtype": triggerSubType,  // id,email,phone    first, next     product, provider
                "bonus_amount_list": bonusAmountList,   // amount types
                "deposit_wager_base": depositWagerCal,  // 0 for deposit+bonus, 1 for bonus only
                "master_types": masterType,
            };

            $.ajax({
                type: 'POST',
                url: bonus_create,
                data: {
                    'bonusDict': JSON.stringify(bonusDict),
                },
                success: function (data) {
                    window.location.reload();
                },
                error: function(data){
                   alert(data.status); // the status code
                   alert(data.responseJSON.error); // the message
                }
            });

        });
    });
});


