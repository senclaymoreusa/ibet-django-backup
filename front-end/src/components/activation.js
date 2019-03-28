import React, { Component } from 'react';
import { FormattedMessage } from 'react-intl';
import { NavLink } from 'react-router-dom';
import { connect } from 'react-redux';
import { authCheckState } from '../actions';

class Activation extends Component {

    componentDidMount() {
        this.props.authCheckState();
    }

    render(){
        return (
          <div>
            <FormattedMessage id="activation.message" defaultMessage='An email with an activation link has been sent to your email address' />
            <br/> 
            <NavLink to='/' style={{ textDecoration: 'none' }}><FormattedMessage id="profile.back" defaultMessage='Back' /></NavLink>
          </div>
        )
    }
}

export default connect(null, {authCheckState})(Activation);