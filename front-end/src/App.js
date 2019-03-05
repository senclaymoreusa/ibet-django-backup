import React, { Component } from 'react';
import { connect } from 'react-redux';
//import logo from './logo.svg';
import './App.css';
import { BrowserRouter as Router } from 'react-router-dom';
import BaseRouter from './routes';
import { IntlProvider } from 'react-intl';
import { messages } from './components/messages';
import { getLanguage } from './actions/language';

class App extends Component {

  // constructor() {
  //   this.store = createStore(reducers, {}, applyMiddleware(ReduxThunk));
  // }

  state = {
    lang: 'zh',
  }

  componentDidMount() {
    this.props.getLanguage();
  }

  render() {
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
  return {
      lang: state.language.lang,
  }
}

export default connect(mapStateToProps, { getLanguage })(App);
