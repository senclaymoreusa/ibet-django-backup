const INITIAL_STATE ={
    game_type: ''
}

export default (state = INITIAL_STATE, action) => {
    switch (action.type) {
      case 'GAME_TYPE':
        return { ...state, game_type: action.payload };
      default:
        return state;
    }
  };
