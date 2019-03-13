import React, { Component } from 'react';
import Navigation from "./navigation";
import { connect } from 'react-redux';
import { authCheckState } from '../actions';
import { FormattedMessage } from 'react-intl';

class Home extends Component {
  
  componentDidMount() {
    
    this.props.authCheckState()

  }

  render() {
      return (
        <div className="rows">
          <div> 
            <Navigation />
          </div>

          <div> 
              <h1> <FormattedMessage id="home.title" defaultMessage='Claymore' /></h1>
          </div>
         
        </div>
      );
    }
  }

  
  export default connect(null, {authCheckState})(Home);