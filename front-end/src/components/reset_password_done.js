import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import { FormattedMessage } from 'react-intl';

class Reset_Password_Done extends Component {
    render(){
        return(
            <div> 
                <div>
                    <FormattedMessage id="reset_password_done.change_confirm" defaultMessage='You have successfully reset your password' />
                </div>
                <div>
                    <FormattedMessage id="reset_password_done.back" defaultMessage='Back to' /><NavLink to='/' style={{ textDecoration: 'none', color: 'blue' }}> 
                    <FormattedMessage id="reset_password_done.home" defaultMessage='Home page' /></NavLink>
                </div>
            </div>
        ) 
    }
}

export default Reset_Password_Done;