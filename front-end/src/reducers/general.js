const INITIAL_STATE ={
    game_type: '',
    game_detail: {},
    term: ''
}

export default (state = INITIAL_STATE, action) => {
    switch (action.type) {
      case 'GAME_TYPE':
        return { ...state, game_type: action.payload };
      case 'GAME_DETAIL':
        return { ...state, game_detail: action.payload };
      case 'TERM_CHANGED':
        return {...state, term: action.payload}
      default:
        return state;
    }
  };
