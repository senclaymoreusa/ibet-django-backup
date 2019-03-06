const INITIAL_STATE ={
    lang: 'en'
}

export default (state = INITIAL_STATE, action) => {
    switch (action.type) {
      case 'SET_LANGUAGE':
        return {...state, lang: action.lang};
      default:
        return state;
    }
  };