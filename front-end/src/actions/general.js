export const game_type = (text) => {
    return {
      type: 'GAME_TYPE',
      payload: text
    };
};

export const game_detail = (game) => {
  return {
    type: 'GAME_DETAIL',
    payload: game
  };
};

export const handle_search =(term) => {
  return {
    type: 'TERM_CHANGED',
    payload: term
  }
}

