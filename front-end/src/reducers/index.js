import { combineReducers } from 'redux';
import GeneralReducer from './general';
import AuthReducer from './auth';

export default combineReducers({
  general: GeneralReducer,
  auth: AuthReducer
});
