import authReducer from '../auth';

import { authStart, authSuccess, authFail, logout } from './../../actions/auth'


describe('Auth Reducer', () => {

    const INITIAL_STATE ={
        token: null,
        error: null, 
        loading: false
    };

    it('should return INITIAL_STATE', () => {
        const curState = authReducer(undefined, {});
        expect(curState).toEqual(INITIAL_STATE);
    });

    it('should return error: null, loading: true for AUTH_START', () => {
        const curState = authReducer(INITIAL_STATE, authStart());
        const expectState = {
            token: null,
            error: null,
            loading: true
        };
        expect(curState).toEqual(expectState);
    });

    it('should return token: action.token, error: null, loading: false for AUTH_SUCCESS', () => {
        const curState = authReducer(INITIAL_STATE, authSuccess());
        const expectState = {
            token: authSuccess.token,
            error: null,
            loading: false
        };
        expect(curState).toEqual(expectState);
    });

    it('should return error: action.error, loading: false for AUTH_FAIL', () => {
        const curState = authReducer(INITIAL_STATE, authFail());
        const expectState = {
            token: null,
            error: authFail().error,
            loading: false
        };
        expect(curState).toEqual(expectState);
    });

    it('should return token: null for AUTH_LOGOUT', () => {
        const curState = authReducer(INITIAL_STATE, logout());
        const expectState = {
            error: null,
            loading: false,
            token: null
        };
        expect(curState).toEqual(expectState);
    });
});