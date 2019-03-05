import React, { Component } from 'react';
import { FormattedMessage } from 'react-intl';

class Email_Sent extends Component {
    render(){
        return <div> <FormattedMessage id="email_sent.message" defaultMessage='An email has been sent to you email address to reset your password' /></div>
    }
}

export default Email_Sent;