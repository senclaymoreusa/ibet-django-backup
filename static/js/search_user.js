import { API_URL } from './config.js';

;(function($){
$("#user-search").on('keyup', function (e) {
    if( this.value.length < 2 ) return;
    var doamin = e.view.location.origin;
    searchOpen(doamin);
});

function searchOpen(doamin) {
    // var domain = "{{ DOMAIN }}";
    var search = $('#user-search').val();
    var block = '';
    // console.log(API_URL);
    var url = doamin + "/users/api/userSearch/?search=" + search + "&block=" + block;
    // console.log(url);
    $.ajax({
        url: url,
        type: 'GET',
        success: function (data) {
            // console.log(data);
            searchResult(data, search, doamin);
        },
        error: function () {
            // console.log('error');
        }

    });
}

function searchResult(data, term, domain) {
    
    var ids = data['id'];
    var usernames = data['username'];
    var emails = data['email'];
    var phones = data['phone'];
    var firstNames = data['firstName'];
    var lastNames = data['lastName'];

    var url = $('#userDetailUrl').val();
    
    var sourceList = [];
    if ($.isNumeric(term)) {
        if (ids.length > 0) {
            sourceList.push({
                'type': 'category',
                'label': term,
                'value': 'MEMBER RESULTS'
            });
            for (var i = 0; i < ids.length; i++) {
                sourceList.push({
                    'type': 'username',
                    'label': term,
                    'value': ids[i]['id'],
                    'id': ids[i]['id']
                });
            }
        }
    } else {
        if (usernames.length > 0) {
            sourceList.push({
                'type': 'category',
                'label': term,
                'value': 'MEMBER RESULTS'
            });

            for (var i = 0; i < usernames.length; i++) {
                sourceList.push({
                    'type': 'username',
                    'label': term,
                    'value': usernames[i]['username'],
                    'id': usernames[i]['id'],
                });
            }
        }
    }
    if (emails.length > 0 || phones.length > 0 || firstNames.length > 0 || lastNames.length > 0) {
        sourceList.push({
            'type': 'category',
            'label': term,
            'value': 'MEMBER DETAILS RESULTS'
        });
    }
    if (emails.length > 0) {
        for (var i = 0; i < emails.length; i++) {
            sourceList.push({
                'type': 'email',
                'label': term,
                'value': emails[i]['email'],
                'id': emails[i]['id'],
            });
        }
    }
    if (phones.length > 0) {
        for (var i = 0; i < phones.length; i++) {
            sourceList.push({
                'type': 'phone',
                'label': term,
                'value': phones[i]['phone'],
                'id': phones[i]['id'],
            });
        }  
    }
    if (firstNames.length > 0) {
        for (var i = 0; i < firstNames.length; i++) {
            sourceList.push({
                'type': 'name',
                'label': term,
                'value': firstNames[i]['firstName'],
                'id': firstNames[i]['id'],
            });
        }
    }
    if (lastNames.length > 0) {
        for (var i = 0; i < lastNames.length; i++) {
            sourceList.push({
                'type': 'name',
                'label': term,
                'value': lastNames[i]['lastName'],
                'id': lastNames[i]['id'],
            });
        }
    }
    // console.log(sourceList);
    
    $( "#user-search" ).autocomplete({
        source: sourceList,
        create: function () {
            $(this).data('ui-autocomplete')._renderItem = function (ul, item) {
                if (item.type === 'category') {
                    return $('<li class="ui-state-disabled member-search-result" style="margin: 0px 13px;">')
                    .append(item.value)
                    .appendTo(ul);
                    // ul.append("<li class='ui-autocomplete-group'>" + item.value + "</li>");
                } else {
                    // var url = "{% url 'xadmin:user_detail' 123 %}".replace('123', item.id);
                    var newUrl = domain + url + item.id;
                    // console.log(newUrl);
                    // console.log(newUrl);
                    if (item.type == 'username') {
                        return $('<li>')
                        .append('<div style="margin: 0px 13px; color:blue;"><a href="' + newUrl + '"><i class="fa fa-user" style="padding: 7px; font-size: 0.83em;" aria-hidden="true"></i>' + item.value + '</a></div>')
                        .appendTo(ul);
                    } else if (item.type == 'email') {
                        return $('<li>')
                        .append('<div style="margin: 0px 13px;"><a href="' + newUrl + '"><i class="fa fa-envelope"  style="padding: 7px; font-size: 0.83em;" aria-hidden="true"></i>' + item.value + '</a></div>')
                        .appendTo(ul);
                    } else if (item.type == 'phone') {
                        return $('<li>')
                        .append('<div style="margin: 0px 13px;"><a href="' + newUrl + '"><i class="fa fa-phone"  style="padding: 7px; font-size: 0.83em;" aria-hidden="true"></i>' + item.value + '</a></div>')
                        .appendTo(ul);
                    } else if (item.type == 'name') {
                        return $('<li>')
                        .append('<div style="margin: 0px 13px;"><a href="' + newUrl + '"><i class="fas fa-id-card" style="padding: 7px; font-size: 0.83em;" aria-hidden="true"></i>' + item.value + '</a></div>')
                        .appendTo(ul);
                    }
                }
            };
        }
    });
}

$("#search-btn-icon").click(function(e){
    var doamin = e.view.location.origin;
    var pageSize = $("#pagination_value").val();
    var search = $('#user-search').val();
    var block = false;
    window.location.href = getUserListRedirectUrl(pageSize, 0, block, search, doamin);
});

function getUserListRedirectUrl(pageSize, offset, block, search, doamin) {
    var curUrl = doamin + "/xadmin/users/";
    // console.log(curUrl);
    var parts = curUrl.split('?');
    // console.log(parts);
    
    var redirectUrl = parts[0]; 
    if (pageSize) {
        redirectUrl += "&pageSize=" + pageSize;
    }
    if (search) {
        redirectUrl += '?search=' + search;
    }
    if (offset) {
        redirectUrl += '?offset=' + offset;
    }
    if (block) {
        redirectUrl += '?block=' + block;
    }
    // console.log(redirectUrl);
    return redirectUrl;
}

})(jQuery)