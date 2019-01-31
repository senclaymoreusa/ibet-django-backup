const INITIAL_STATE ={
    game_type: '',
    game_detail: {}
}

export default (state = INITIAL_STATE, action) => {
    switch (action.type) {
      case 'GAME_TYPE':
        return { ...state, game_type: action.payload };
      case 'GAME_DETAIL':
        return { ...state, game_detail: action.payload };
      default:
        return state;
    }
  };
