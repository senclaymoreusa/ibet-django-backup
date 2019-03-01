import axios from "axios";
const API_URL = process.env.REACT_APP_REST_API;

const setLanguageState = (language) => {
    return {
        type: 'SET_LANGUAGE',
        lang: language
    }
}

export const setLanguage = (language) => {
    const config = {
        headers: {
            'Content-Type': 'application/json',
        },
        withCredentials: true,
    };

    return (dispatch) => {
        return axios.post(API_URL + 'users/api/language/', {
            languageCode: language
        }, config)
        .then(res => {
            // let result = res;
            // return axios.get(API_URL + 'users/api/language/', config)
            // .then(res => {
            //     console.log(res);
            //     return Promise.resolve(result);
            // })
            if (language.indexOf('zh') >= 0) {
                language = 'zh';
            }
            dispatch(setLanguageState(language));
            return Promise.resolve(res);
        })
        .catch(err => {
            console.log(err.response);
            return Promise.reject(err.response);
        })
    }
}


export const getLanguage = () => {
    return (dispatch) => {
        return axios.get(API_URL + 'users/api/language/')
        .then(res => {
            console.log(res);
            dispatch(setLanguageState(res.data.languageCode));
            return Promise.resolve(res.data.languageCode);
        })
        .catch(err => {
            console.log(err.response);
            return Promise.reject(err.response);
        })
    }
}