const INITIAL_STATE ={
    token: null,
    error: null, 
    loading: false,
    block: false
}

export default (state = INITIAL_STATE, action) => {
    switch (action.type) {
      case 'AUTH_START':
        return {...state, error: null, loading: true};
      case 'AUTH_SUCCESS':
        return {...state, token: action.token, error: null, loading: false, block: false};
      case 'AUTH_FAIL':
        return {...state, error: action.error, loading: false};
      case 'AUTH_LOGOUT':
        return {...state, token: null};
        case 'AUTH_BLOCK':
      return {...state, block: true};
      default:
        return state;
    }
  };
