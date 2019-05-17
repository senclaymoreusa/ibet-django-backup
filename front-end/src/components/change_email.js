import React, { Component } from 'react';
import { config } from "../util_config";
import axios from 'axios';
import { withRouter } from 'react-router-dom';
import { FormattedMessage } from 'react-intl';
import { errors } from './errors';


const API_URL = process.env.REACT_APP_REST_API;

class Change_Email extends Component {
    constructor(props){
        super(props);
        
        this.state = {
            new_email: '',
            confirm_email: '',
            errorCode: '',
            fetched_data: {},

            live_check_email: false,
            live_check_email_match: false,

            email_existed_error: false,

            button_disable: true
        }

        this.onInputChange_new_email     = this.onInputChange_new_email.bind(this);
        this.onInputChange_confirm_email = this.onInputChange_confirm_email.bind(this);
        this.onFormSubmit                   = this.onFormSubmit.bind(this);
    }

    async componentDidMount() {
      const token = localStorage.getItem('token');
      config.headers["Authorization"] = `Token ${token}`;

      await axios.get(API_URL + 'users/api/user/', config)
        .then(res => {
            this.setState({fetched_data: res.data});
        })
    }

    onInputChange_new_email(event){
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        if (!event.target.value.match(re)){
            this.setState({live_check_email: true, button_disable: true})
        }else{
            this.setState({live_check_email: false})
            this.check_button_disable()
        }
        if (this.state.confirm_email){
            if (this.state.confirm_email !== event.target.value){
                this.setState({live_check_email_match: true, button_disable: true})
            }
        }
        if (this.state.confirm_email === event.target.value && event.target.value.match(re)){
            this.setState({ button_disable: false, live_check_email_match: false})
        }
        this.setState({new_email: event.target.value});
    }
    
    onInputChange_confirm_email(event){
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        if (this.state.new_email !== event.target.value){
            this.setState({live_check_email_match: true, button_disable: true})
        }else if(!event.target.value.match(re)){
            this.setState({button_disable: true})
            if (this.state.new_email === event.target.value){
                this.setState({live_check_email_match: false})
            }
        }else{
            this.setState({live_check_email_match: false, button_disable: false})
        }
        this.setState({confirm_email: event.target.value});
    }

    check_button_disable(){
        if (!this.live_check_email && this.state.new_email && this.state.confirm_email && this.state.confirm_email === this.state.new_email){
          this.setState({button_disable: false})
        }
      }
    
    onFormSubmit(event){
        event.preventDefault();
        
        this.setState({email_existed_error: false})

        const token = localStorage.getItem('token');
        config.headers["Authorization"] = `Token ${token}`;

        axios.post(API_URL + `users/api/updateemail/`, {
            old_email: this.state.fetched_data.email,
            new_email: this.state.new_email
        }, config)
        .then(res => {
            if (res.data === 'Duplicate'){
                this.setState({email_existed_error: true})
            }else{
                axios.get(API_URL + `users/api/sendemail/?case=change_email&to_email_address=${this.state.fetched_data.email}&email=${this.state.new_email}`, config)
                .then(res => {
                    axios.get(API_URL + `users/api/sendemail/?case=change_email&to_email_address=${this.state.new_email}&&email=${this.state.new_email}`, config)
                })
                
                this.props.history.push("/profile");
            }
        })
    }
    render(){


        const showErrors = () => {
            if (this.state.errorCode === errors.EMAIL_NOT_MATCH) {
                return (
                    <div style={{color: 'red'}}> 
                        <FormattedMessage id="change_email.email_not_match" defaultMessage='Email does not match' /> 
                    </div>
                );
            } else if (this.state.errorCode === errors.EMAIL_CAN_NOT_BE_SAME) {
                return (
                    <div style={{color: 'red'}}> 
                        <FormattedMessage id="change_email.email_can_not_be_same" defaultMessage='New email address has to be different from the old email address' /> 
                    </div>
                );
            }
        }
        return (
            <div>
                <form onSubmit={this.onFormSubmit} >

                    <div>
                        <label><b>
                        <FormattedMessage id="change_email.enter_email" defaultMessage='New Email address: ' />    
                        </b></label>
                        <input
                            placeholder="example@gmail.com"
                            className="form-control"
                            value={this.state.new_email}
                            onChange={this.onInputChange_new_email}
                        />
                    </div>

                    {this.state.live_check_email && <div style={{color: 'red'}}> <FormattedMessage  id="error.email" defaultMessage='Email address not valid' /> </div>}

                    {this.state.email_existed_error && <div style={{color: 'red'}}> <FormattedMessage  id="referral.email_exist" defaultMessage='This email has already been registerd' /> </div>}
                    
                    <div>
                        <label><b>
                        <FormattedMessage id="change_email.confirm_email" defaultMessage='Confirm Email address: ' />
                        </b></label>
                        <input
                            placeholder="example@gmail.com"
                            className="form-control"
                            value={this.state.confirm_email}
                            onChange={this.onInputChange_confirm_email}
                        />
                    </div>

                    {this.state.live_check_email_match && <div style={{color: 'red'}}> <FormattedMessage id="change_email.email_not_match" defaultMessage='Email does not match' />  </div>}

                    <span className="input-group-btn">
                        <button disabled = {this.state.button_disable} type="submit" className="btn btn-secondary"> 
                        <FormattedMessage id="change_email.sumbit" defaultMessage='Submit' />    
                        </button>
                    </span>

                    <button style={{color: 'red'}} onClick={()=>{this.props.history.push("/update_profile")}}> 
                        <FormattedMessage id="change_email.cancel" defaultMessage='Cancel' />       
                    </button>
                </form>
                {
                    showErrors()
                }
            </div>
        )
    }
}

export default withRouter(Change_Email);