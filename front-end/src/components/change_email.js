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
            fetched_data: {}
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
        this.setState({new_email: event.target.value});
    }
    
    onInputChange_confirm_email(event){
        this.setState({confirm_email: event.target.value});
    }
    
    onFormSubmit(event){
        event.preventDefault();
        
        if (this.state.new_email !== this.state.confirm_email) {
            this.setState({errorCode: errors.EMAIL_NOT_MATCH});
        } else if(this.state.new_email === this.state.fetched_data.email){
            this.setState({errorCode: errors.EMAIL_CAN_NOT_BE_SAME});
        } else if (this.state.new_email === this.state.confirm_email){
            const token = localStorage.getItem('token');
            config.headers["Authorization"] = `Token ${token}`;
            
            const body = JSON.stringify({
                username:         this.state.fetched_data.username,
                email:            this.state.new_email,
                first_name:       this.state.fetched_data.first_name,
                last_name:        this.state.fetched_data.last_name,
                phone:            this.state.fetched_data.phone,
                date_of_birth:    this.state.fetched_data.date_of_birth,
                street_address_1: this.state.fetched_data.street_address_1,
                street_address_2: this.state.fetched_data.street_address_2,
                country:          this.state.fetched_data.country,
                city:             this.state.fetched_data.city,
                zipcode:          this.state.fetched_data.zipcode,
                state:            this.state.fetched_data.state
            })
             
            axios.put(API_URL + 'users/api/user/', body, config)
            
            axios.get(API_URL + `users/api/sendemail/?case=change_email&to_email_address=${this.state.fetched_data.email}&email=${this.state.new_email}`, config)
            .then(res => {
                axios.get(API_URL + `users/api/sendemail/?case=change_email&to_email_address=${this.state.new_email}&&email=${this.state.new_email}`, config)
            })
            
            this.props.history.push("/profile");
        }
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

                    <span className="input-group-btn">
                        <button type="submit" className="btn btn-secondary"> 
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