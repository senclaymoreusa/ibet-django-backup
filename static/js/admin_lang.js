import { API_URL, config } from './config.js';

$(document).ready(function() {
    axios.get(API_URL + 'users/api/language/', config)
    .then(res => {
        let language = res.data.languageCode;
        $('#language-select').val(language);    
    });
});

$("#language-select").change(function(){
    return axios.post(API_URL + 'users/api/language/', {
            languageCode: $("#language-select").val()
        }, config)
        .then(res => {
            location.reload();
        });
});