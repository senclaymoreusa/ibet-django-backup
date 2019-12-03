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

    $('#bonus_status_filter, #bonus_type_filter').change(function(){
        bonus_table.draw();
    });

    $('#bonus-search-btn').click(function(){
        bonus_table.draw();
    });

    var productList = ["casino", "live-casino", "sports", "lottery"]

    var dataTarget;

    // bonus 01
    var bonusName;
    var bonusStartTime;
    var bonusEndTime;

    //bonus 02
    var masterType = [];
    var bonusCategory;
    var issued;

    //manual bonus
    //bonus 03
    var bonusAmount;
    var wagerMasterValue = 0;
    var wagerList = [];     //admin
    var timeLimit = -1;     //admin

    //bonus 05
    var targetAll;
    var targetAudience;
    var bonusRequirements;
    var excludedGroups;

    // triggered bonus
    var triggerType;
    var triggerSubType;
    var providerChosen;

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
        }else{
            $('#bonus-next-02').attr('data-target', '#bonus-04');
        }
    });

    // bonus 03
    $('#verification-bonus').on('change', function(){
        if($(this).is(":checked")){
            triggerType = "verification";
            $('#verification-choices').show();
            $('#deposit-choices').hide();
            $('#turnover-choices').hide();
        }else{
            $('#verification-choices').hide();
        }
    });

    $('#deposit-bonus').on('change', function(){
        if($(this).is(":checked")){
            triggerType = "deposit";
            $('#deposit-choices').show();
            $('#verification-choices').hide();
            $('#turnover-choices').hide();
        }else{
            $('#deposit-choices').hide();
        }
    });

    $('#turnover-bonus').on('change', function(){
        if($(this).is(":checked")){
            triggerType = "turnover";
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

    $('#provider-selector').chosen({width: "172px"}).change(function(){
        $('#turnover-choices-provider').prop('checked', true);
        providerChosen = $("#provider-selector").chosen().val();
    });

    // bonus 04
    $('#bonus-amount').on('change', function(){
        bonusAmount = parseFloat($(this).val()).toFixed(2);
        $(this).prop('value', bonusAmount);
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

    $('#time-period').on('change', function(){
        timeLimit = $(this).val();
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
        if($(this).is(':checked')){
            $(".wager-product").prop("checked", "checked");
        }else{
            $(".wager-product").prop("checked", "");
        }
        for(var i = 0; i < productList.length; i++){
            var curProduct = productList[i];
            wagerSelect(document.getElementById("wager-" + curProduct), curProduct);
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
        if($.isNumeric(wagerValue) && $.isNumeric(bonusAmount)){
            var hasMasterSingle = masterType.includes("casino") || masterType.includes("live-casino")
            || masterType.includes("sports");
            if(masterType.includes(name) || !hasMasterSingle){
                var str = " x " + bonusAmount + " = " + wagerValue * bonusAmount;
                wagerMasterValue = wagerValue;
                $('#wager-' + name + '-total').attr('value', str);
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
        bonusRequirements = $(this).chosen().val();
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
        updateDataTarget(cur);
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
        bonusName = $('#bonus-name').val();
        bonusStartTime = $('#bonus-start-time').val();
        bonusEndTime = $('#bonus-end-time').val();

        bonusEndTime = new Date(bonusEndTime);
	    bonusEndTime.setDate(bonusEndTime.getDate() + 1);

        checkEmpty(this);
    });

    $('#bonus-next-02').on('click', function(){
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
            }else{

            }

        });
        if($('#bonus-issue').is(":checked")){
            issued = "checked";
        }else{
            issued = "unchecked";
        }
        updateDataTarget(this);

        if(!$("input:radio[name='bonus-category']").is(":checked") ||
        !$("input:checkbox[name='master-type']").is(":checked")){
            showErrorMsg(this);
        }else{
            removeErrorMsg(this);
        }
    });

    $('#bonus-next-03').on('click', function(){
        if(triggerType == "verification"){
            triggerSubType = $("input[name='verification-choice']").val();
        }else if(triggerType == "deposit"){
            triggerSubType = $("input[name='deposit-choice']").val();
        }else if(triggerType == "turnover"){
            var turnoverChoice = $("input[name='turnover-choice']:checked").val();
            if(turnoverChoice == "product"){
                triggerSubType = $("#product-selector").val();
            }else if(turnoverChoice == "provider"){
                triggerSubType = providerChosen;
            }
        }
        updateDataTarget(this);
        if(typeof triggerType === typeof undefined || typeof triggerSubType === typeof undefined) {
            showErrorMsg(this);
        }else{
            removeErrorMsg(this, $(this).attr('data-target'));
        }
    });

    $('#bonus-next-04').on('click', function(){
        if(checkEmpty(this) == true){
            for(var i = 0; i < productList.length; i++){
            var curBox = $('#wager-' + productList[i]);
                if(curBox.is(':checked')){
                    if(curBox.is(':disabled')){
                        wagerList[i] = $('#wager-' + productList[i] + '-times').val();
                    }else{
                        var subWager = $('#wager-' + productList[i] + '-total').val().split(' ');
                        wagerList[i] = subWager[3].substring(0, subWager[3].length - 1);
                    }
                }else{
                    wagerList[i] = -1;
                }
            }
        }
        console.log(wagerList)
    });

    $('#bonus-next-05').on('click', function(){

        updateDataTarget(this);

        // check empty, either openAll or selectGroup should be true, selectMustHave must be true
        targetAll = $('#open-to-all').is(':checked');
        var selectGroup = $('#specific-accounts').is(':checked') && $('#group-assigned').val() !== null;
        var selectMustHave = $('#bonus-requirements').val() !== null;
        if((!targetAll && !selectGroup) || !selectMustHave){
            showErrorMsg(this);
        }else{
            removeErrorMsg(this);
        }

    });

    $('#bonus-next-06').on('click', function(){
        if(checkEmpty(this) == true){
            maxDailyTimes = $('#daily-claim').val();
            maxTotalTimes = $('#total-claim').val();
            maxAssociatedAccounts = $('#associated-total-claim').val();
            maxUser = $('#maximum-claimer').val();
            maxUserAmount = $('#max-user-amount').val();
            maxTargetUserAmount = $('#max-target-user-amount').val();
        }
    });

    $('#publish').on('click', function () {
        $('#publish').html('Click to Publish');
        $('#publish').attr('id', 'publish-confirm');
        $('#publish-confirm').on('click', function(){
            var bonusDict = {
                "name": bonusName,
                "startTime": formatDatetime(bonusStartTime),
                "endTime": formatDatetime(bonusEndTime.getDate() + 1),
                "masterType": masterType,       // wager master type list
                "category": bonusCategory,      // "manual" or "triggered"
                "issued": issued,
                "amount": bonusAmount,
                "wagerMultiple": wagerList,     // wager product multiple
                "timeLimit": timeLimit,
                "target": targetAll,
                "targetPlayer": targetAudience,
                "requirements": bonusRequirements,
                "excludedPlayer": excludedGroups,
                "maxDailyTimes": maxDailyTimes,
                "maxTotalTimes": maxTotalTimes,
                "maxAssociatedAccounts": maxAssociatedAccounts,
                "maxUser": maxUser,
                "maxUserAmount": maxUserAmount,
                "maxTargetUserAmount": maxTargetUserAmount,
                "deliveryMethod": $("input[name='delivery']").val()
            };

            console.log(bonusDict)

            $.ajax({
                type: 'POST',
                url: bonus_admin,
                data: {
                    'type': 'newBonus',
                    'bonusDict': JSON.stringify(bonusDict),
                },
                success: function (data) {
                    window.location.reload();
                },
            });

        });
    });
});


