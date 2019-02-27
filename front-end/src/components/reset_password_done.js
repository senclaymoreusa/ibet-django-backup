import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import { messages } from './messages';

class Reset_Password_Done extends Component {
    render(){
        return(
            <div> 
                <div>
                  {messages.CHANGE_PASSOWRD_CONFIRM} 
                </div>
                <div>
                  Back to <NavLink to='/' style={{ textDecoration: 'none', color: 'blue' }}> Home page </NavLink>
                </div>
            </div>
        ) 
    }
}

export default Reset_Password_Done;