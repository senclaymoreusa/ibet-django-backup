import axios from "axios";

const API_URL = process.env.REACT_APP_REST_API

export const AUTH_RESULT_SUCCESS = 0;
export const AUTH_RESULT_FAIL = 1;

export const authStart = () => {
    return {
      type: 'AUTH_START'
    }
  }
  
  export const authSuccess = (token) => {
    return {
      type: 'AUTH_SUCCESS',
      token: token
    }
  }
  
  export const authFail = (error) => {
    return {
      type: 'AUTH_FAIL',
      error: error
    }
  }
  
  export const authLogin = (username, password) => {
    return (dispatch) => {
        dispatch(authStart());
        return axios.post(API_URL + 'users/api/login/', {
            username: username,
            password: password
        })
        .then(res => {
            const token = res.data.key;
            if (!token || token === "undefined") {
                dispatch(logout());
            }
            const expirationDate = new Date(new Date().getTime() + 3600 * 1000);
            localStorage.setItem('token', token);
            localStorage.setItem('expirationDate', expirationDate);
            dispatch(authSuccess(token));
            dispatch(checkAuthTimeout(3600));
            return Promise.resolve();
        })
        .catch(err => {
            dispatch(authFail(err.response.data.detail))
            return Promise.reject(err.response.data.detail);
        })
        
    }
  }


  export const authSignup = (username, email, password1, password2, first_name, last_name, phone, date_of_birth, street_address_1, street_address_2, country, city, zipcode, state) => {
    return dispatch => {
        dispatch(authStart());
        const config = {
          headers: {
            "Content-Type": "application/json"
          }
        };
        const body = JSON.stringify({ username, email, password1, password2, first_name, last_name, phone, date_of_birth,
          street_address_1, street_address_2, country, city, zipcode, state
        });

        return axios.post(API_URL + 'users/api/signup/', body, config)
        .then(res => {
            const token = res.data.key;
            const expirationDate = new Date(new Date().getTime() + 3600 * 1000);
            localStorage.setItem('token', token);
            localStorage.setItem('expirationDate', expirationDate);
            dispatch(authSuccess(token));
            dispatch(checkAuthTimeout(3600));
            return Promise.resolve()
        })
        .catch(err => {
            dispatch(authFail(err))
            return Promise.reject(err)
        })
    }
}
  
  export const checkAuthTimeout = expirationTime => {
    return dispatch => {
        setTimeout(() => {
            dispatch(logout());
        }, expirationTime * 1000)
    }
  }
  
  export const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('expirationDate');
    return {
        type: 'AUTH_LOGOUT'
    };
  }

  export const isBlock = () => {
      return {
        type: 'AUTH_BLOCK'
      }
  }

  export const authCheckState = () => {
    return dispatch => {
        const token = localStorage.getItem('token');
        if (!token || token === "undefined") {
            // check token first
            dispatch(logout());
            return Promise.resolve(AUTH_RESULT_FAIL);
        } else {
            // check token expiration time
            const expirationDate = new Date(localStorage.getItem('expirationDate'));
            if ( expirationDate <= new Date() ) {
                dispatch(logout());
                return Promise.resolve(AUTH_RESULT_FAIL);
            } else {
                // check whether user is blocked
                const config = {
                    headers: {
                    "Content-Type": "application/json"
                    }
                };
                config.headers["Authorization"] = `Token ${token}`;
        
                return axios.get(API_URL + 'users/api/user/', config)
                .then(res => {
                    if (res.data.block) {
                        dispatch(logout());
                        return Promise.resolve(AUTH_RESULT_FAIL);
                    } else {
                        dispatch(authSuccess(token));
                        dispatch(checkAuthTimeout( (expirationDate.getTime() - new Date().getTime()) / 1000) );
                        return Promise.resolve(AUTH_RESULT_SUCCESS);
                    }
                })
                .catch(err => {
                    dispatch(authFail(err.response.data.detail))
                    return Promise.resolve(AUTH_RESULT_FAIL);
                });
            }
        }
    }
}  