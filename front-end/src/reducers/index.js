import { combineReducers } from 'redux';
import GeneralReducer from './general';
import AuthReducer from './auth';
import LanguageReducer from './language';

export default combineReducers({
  general: GeneralReducer,
  auth: AuthReducer,
  language: LanguageReducer,
});
