import React, { Component } from 'react';
import { FormattedMessage } from 'react-intl';
import { NavLink } from 'react-router-dom';

class Email_Sent extends Component {
    render(){
        return (
            <div> 
                <FormattedMessage id="email_sent.message" defaultMessage='An email has been sent to you email address to reset your password' />
                <div>
                    <NavLink to='/' style={{ textDecoration: 'none', color: 'blue' }}> 
                        <FormattedMessage id="reset_password_done.home" defaultMessage='Home page' />
                    </NavLink>
                </div>
            </div>
        )
    }
}

export default Email_Sent;