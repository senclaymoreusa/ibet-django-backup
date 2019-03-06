import axios from "axios";
import { config } from "../util_config";
const API_URL = process.env.REACT_APP_REST_API;

const setLanguageState = (language) => {
    return {
        type: 'SET_LANGUAGE',
        lang: language
    }
}

// const config = {
//     headers: {
//         'Content-Type': 'application/json',
//     },
//     withCredentials: true,
// };

export const setLanguage = (language) => {
    
    return (dispatch) => {
        return axios.post(API_URL + 'users/api/language/', {
            languageCode: language
        }, config)
        .then(res => {
            if (language.indexOf('zh') >= 0) {
                language = 'zh';
            }
            dispatch(setLanguageState(language));
            return Promise.resolve(res);
        })
        .catch(err => {
            // console.log(err.response);
            return Promise.reject(err.response);
        })
    }
}


export const getLanguage = () => {
    return (dispatch) => {
        return axios.get(API_URL + 'users/api/language/', config)
        .then(res => {
            let language = res.data.languageCode;
            if (language.indexOf('zh') >= 0) {
                language = 'zh';
            }
            // console.log(res);
            dispatch(setLanguageState(language));
            return Promise.resolve(language);
        })
        .catch(err => {
            // console.log(err.response);
            return Promise.reject(err.response);
        })
    }
}