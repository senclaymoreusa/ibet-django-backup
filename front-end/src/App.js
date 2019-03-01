import React, { Component } from 'react';
import { connect } from 'react-redux';
//import logo from './logo.svg';
import './App.css';
import { BrowserRouter as Router } from 'react-router-dom';
import BaseRouter from './routes';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware } from 'redux';
import ReduxThunk from 'redux-thunk';
import reducers from './reducers';
import {IntlProvider, FormattedMessage} from 'react-intl';
import { messages } from './components/messages';
import { setLanguage } from './actions/language';

class App extends Component {

  // constructor() {
  //   this.store = createStore(reducers, {}, applyMiddleware(ReduxThunk));
  // }

  state = {
    lang: 'zh',
  }

  render() {
    const store = createStore(reducers, {}, applyMiddleware(ReduxThunk));
    const { lang } = this.props; 
    return (
      // <Provider store={this.store}>
      <IntlProvider locale={lang} messages={messages[lang]}>
        <Router>
          <BaseRouter />
        </Router>
      </IntlProvider>
      // </Provider>
    );
  }
}

// export default App;

const mapStateToProps = (state) => {
  console.log('state changed:' + state.language.lang);
  return {
      lang: state.language.lang,
  }
}

export default connect(mapStateToProps, {setLanguage})(App);
