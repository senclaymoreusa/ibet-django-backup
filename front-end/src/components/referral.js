import React from 'react';
import axios from 'axios';
import { config } from '../util_config';
import { NavLink } from 'react-router-dom';
import { FormattedMessage } from 'react-intl';

const API_URL = process.env.REACT_APP_REST_API;

class Referral extends React.Component {
    constructor(props){
        super(props);
    
        this.state = {
          data: '',
          email: '',
          error: ''
        };

        this.onInputChange_email            = this.onInputChange_email.bind(this);
        this.onFormSubmit                   = this.onFormSubmit.bind(this);
    }

    componentDidMount() {
        const token = localStorage.getItem('token');
          config.headers["Authorization"] = `Token ${token}`;

          axios.get(API_URL + 'users/api/user/', config)
          .then(res => {
              this.setState({data: res.data});
        }) 
    }

    onInputChange_email(event){
        this.setState({email: event.target.value});
    }

    onFormSubmit(event){
        event.preventDefault();
        axios.get(API_URL + `users/api/checkreferral?referral_id=${this.state.data.referral_id}`, config)
        .then(res =>{
            if (res.data === 'Valid'){
                axios.get(API_URL + `users/api/sendemail/?case=referral&to_email_address=${this.state.email}&username=${this.state.data.username}&referralid=${this.state.data.referral_id}`, config)
                .then(res =>{
                    alert('You have successfully referred a User')
                    this.props.history.push('/');
                }).catch(err => {
                    console.log(err.response)
                })
            }else{
                this.setState({error: 'You have reached the maximum referral number'})
            }
        })
    }

    render(){
        return (
            <div> 
                <form onSubmit={this.onFormSubmit} >
                    <div>
                        <div>
                            <label><b>
                                Enter the email account you want to refer
                            </b></label>
                        </div>
                        <input
                            placeholder="example@gmail.com"
                            className="form-control"
                            value={this.state.email}
                            onChange={this.onInputChange_email}
                        />
                    </div>

                    <span className="input-group-btn">
                        <button type="submit" className="btn btn-secondary"> 
                            Submit   
                        </button>
                    </span>          

                </form>
                <button className="btn btn-secondary"> 
                    <NavLink to='/' style={{ textDecoration: 'none' }}><FormattedMessage id="profile.back" defaultMessage='Back' /></NavLink> 
                </button>
                {
                    <div style={{color: 'red'}}> {this.state.error} </div>
                }

            </div>
        )
    }
}

export default Referral;