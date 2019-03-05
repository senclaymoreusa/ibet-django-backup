import React, { Component } from 'react';
import axios from 'axios';
import { withRouter } from 'react-router-dom';
import { config } from '../util_config';
import { FormattedMessage } from 'react-intl';


const API_URL = process.env.REACT_APP_REST_API

class Forget_Password extends Component {

    constructor(props){
        super(props);

        this.state = {
           old_email: '',
           success: false
        }

        this.onInputChange_old_email  = this.onInputChange_old_email.bind(this);
        this.onFormSubmit             = this.onFormSubmit.bind(this);
    }

    onInputChange_old_email(event){
        this.setState({old_email: event.target.value});
    }

    onFormSubmit(event){
        event.preventDefault();
        
        // const config = {
        //     headers: {
        //       "Content-Type": "application/json"
        //     }
        // };
      
        const body = {
            email: this.state.old_email
        }

        axios.post(API_URL + 'users/api/reset-password/', body, config)
        .then(res => {
            this.setState({success: true})
            this.props.history.push("/email_sent")
        })
    }

    render(){

        const showErrors = () => {
            if (this.state.success) {
                return (
                    <div style={{color: 'red'}}> 
                        <FormattedMessage id="email_sent.message" defaultMessage='An email has been sent to you email address to reset your password' /> 
                    </div>
                );
            }
        }
        return (
            <div> 
                <div><FormattedMessage id="forget_password.enter_email" defaultMessage='Enter your email address: ' /></div>
                <form onSubmit={this.onFormSubmit} >
                    <label><b>
                    <FormattedMessage id="forget_password.mail" defaultMessage='Email: ' />
                    </b></label>
                    <input
                        placeholder="example@gmail.com"
                        className="form-control"
                        value={this.state.old_email}
                        onChange={this.onInputChange_old_email}
                    />

                    <span className="input-group-btn">
                        <button type="submit" className="btn btn-secondary"> 
                        <FormattedMessage id="forget_password.confirm" defaultMessage='Confirm' />
                        </button>
                    </span>
                </form>

                {
                    // this.state.success  && messages.SEND_EMAIL_MESSAGE
                    showErrors()
                }
                
            </div>
        )
    }
}

export default withRouter(Forget_Password);