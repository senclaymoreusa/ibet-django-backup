import axios from "axios";

const API_URL = process.env.REACT_APP_REST_API

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
    return dispatch => {
        dispatch(authStart());
        axios.post(API_URL + 'rest-auth/login/', {
            username: username,
            password: password
        })
        .then(res => {
            const token = res.data.key;
            const expirationDate = new Date(new Date().getTime() + 3600 * 1000);
            localStorage.setItem('token', token);
            localStorage.setItem('expirationDate', expirationDate);
            dispatch(authSuccess(token));
            dispatch(checkAuthTimeout(3600));
        })
        .catch(err => {
            dispatch(authFail(err))
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

  export const authCheckState = () => {
    return dispatch => {
        const token = localStorage.getItem('token');
        if (token === undefined) {
            dispatch(logout());
        } else {
            const expirationDate = new Date(localStorage.getItem('expirationDate'));
            if ( expirationDate <= new Date() ) {
                dispatch(logout());
            } else {
                dispatch(authSuccess(token));
                dispatch(checkAuthTimeout( (expirationDate.getTime() - new Date().getTime()) / 1000) );
            }
        }
    }
}