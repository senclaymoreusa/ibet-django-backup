import React, { Component } from 'react';

import { messages } from './messages';

class Email_Sent extends Component {
    render(){
        return <div> {messages.SEND_EMAIL_MESSAGE} </div>
    }
}

export default Email_Sent;