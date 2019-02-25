import React, { Component } from 'react';
import axios from 'axios';
import { withRouter } from 'react-router-dom';
import { messages } from './messages';

const API_URL = process.env.REACT_APP_REST_API

class Change_Email extends Component {
    constructor(props){
        super(props);
        
        this.state = {
            new_email: '',
            confirm_email: '',
            fetched_data: {}
        }

        this.onInputChange_new_email     = this.onInputChange_new_email.bind(this);
        this.onInputChange_confirm_email = this.onInputChange_confirm_email.bind(this);
        this.onFormSubmit                   = this.onFormSubmit.bind(this);
    }

    async componentDidMount() {
      const token = localStorage.getItem('token');
      const config = {
        headers: {
          "Content-Type": "application/json"
        }
      };
      config.headers["Authorization"] = `Token ${token}`;

      await axios.get(API_URL + 'users/api/user/', config)
        .then(res => {
            this.setState({fetched_data: res.data})
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
        
        if(this.state.new_email !== this.state.confirm_email){
            alert('Email does not match')
        }
        else if(this.state.new_email === this.state.fetched_data.email){
            alert('New email address has to be different from the old email address!')
        }
        else if (this.state.new_email === this.state.confirm_email){
            const token = localStorage.getItem('token');
            const config = {
            headers: {
                "Content-Type": "application/json"
            }
            };
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
            
            axios.get(API_URL + `users/api/sendemail/?${messages.FROM_EMAIL}&${messages.TO_EMAIL}${this.state.fetched_data.email}&${messages.CHANGE_EMAIL_SUBJECT}&${messages.CHANGE_EMAIL_CONTENT}${this.state.new_email}`)
            .then(res => {
                axios.get(API_URL + `users/api/sendemail/?${messages.FROM_EMAIL}&${messages.TO_EMAIL}${this.state.new_email}&${messages.CHANGE_EMAIL_SUBJECT}&${messages.CHANGE_EMAIL_CONTENT}${this.state.new_email}`)
            })
            
            
            this.props.history.push("/profile")
            alert('You have successful updated you email address!')
        }
    }
    render(){
        return (
            <div>
                <form onSubmit={this.onFormSubmit} >

                    <div>
                        <label><b>New Email address:</b></label>
                        <input
                            placeholder="example@gmail.com"
                            className="form-control"
                            value={this.state.new_email}
                            onChange={this.onInputChange_new_email}
                        />
                    </div>

                    <div>
                        <label><b>Confirm Email address:</b></label>
                        <input
                            placeholder="example@gmail.com"
                            className="form-control"
                            value={this.state.confirm_email}
                            onChange={this.onInputChange_confirm_email}
                        />
                    </div>

                    <span className="input-group-btn">
                        <button type="submit" className="btn btn-secondary"> 
                            Submit 
                        </button>
                    </span>
                    <button style={{color: 'red'}} onClick={()=>{this.props.history.push("/update_profile")}}> 
                        Cancel 
                    </button>
                </form>
            </div>
        )
    }
}

export default withRouter(Change_Email);
