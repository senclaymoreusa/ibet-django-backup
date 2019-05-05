import React, { Component } from 'react';
import axios from 'axios';
import { withRouter } from 'react-router-dom';
import { config } from '../util_config';
import { FormattedMessage } from 'react-intl';
import { errors } from './errors';


const API_URL = process.env.REACT_APP_REST_API;

class Forget_Password extends Component {

    constructor(props){
        super(props);

        this.state = {
           old_email: '',
           success: false,
           errorCode: '',

           button_disable: true,

           live_check_email: '',

           email_not_exist: false
        }

        this.onInputChange_old_email  = this.onInputChange_old_email.bind(this);
        this.onFormSubmit             = this.onFormSubmit.bind(this);
    }

    onInputChange_old_email(event){
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        if (!event.target.value.match(re)){
            this.setState({live_check_email: true, button_disable: true})
        }else{
            this.setState({live_check_email: false, button_disable: false})
        }
        this.setState({old_email: event.target.value, email_not_exist: false});
    }

    onFormSubmit(event){
        event.preventDefault();
      
        const body = {
            email: this.state.old_email
        }

        axios.get(API_URL + `users/api/checkemailexist/?email=${this.state.old_email}`, config)
        .then(res => {
            if (res.data === 'Exist'){
                axios.post(API_URL + 'users/api/reset-password/', body, config)
                .then(res => {
                    this.setState({success: true})
                    this.props.history.push("/email_sent")
                })
                .catch((err) => {
                    this.setState({errorCode: errors.EMAIL_NOT_VALID});
                });
            }else{
                this.setState({email_not_exist: true})
            }
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
            } else if (this.state.errorCode === errors.EMAIL_NOT_VALID) {
                return (
                    <div style={{color: 'red'}}> 
                        <FormattedMessage id="forget_password.email_not_valid" defaultMessage='Email is not valid' /> 
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
                        <button disabled = {this.state.button_disable} type="submit" className="btn btn-secondary"> 
                            <FormattedMessage id="forget_password.confirm" defaultMessage='Confirm' />
                        </button>
                    </span>

                    {this.state.live_check_email && <div style={{color: 'red'}}> <FormattedMessage  id="error.email" defaultMessage='Email address not valid' /> </div>}

                    {this.state.email_not_exist && <div style={{color: 'red'}}> <FormattedMessage  id="forget_password.email_not_valid" defaultMessage='Email does not exsit' /> </div>}
                </form>

                <button style={{color: 'red'}} onClick={ () => {this.props.history.push('/')}}>
                    <FormattedMessage id="login.back" defaultMessage='Back' />
                </button>

                {
                    showErrors()
                }
                
            </div>
        )
    }
}

export default withRouter(Forget_Password);