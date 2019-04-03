import React from 'react';
import axios from 'axios';
import { config } from '../util_config';
import { NavLink } from 'react-router-dom';
import { FormattedMessage, injectIntl } from 'react-intl';

const API_URL = process.env.REACT_APP_REST_API;

class Referral extends React.Component {
    constructor(props){
        super(props);
    
        this.state = {
          data: '',
          email: '',
          error: false
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
        const { formatMessage } = this.props.intl;
        const message = formatMessage({ id: 'referral.user' });

        event.preventDefault();
        axios.get(API_URL + `users/api/checkreferral?referral_id=${this.state.data.referral_id}`, config)
        .then(res =>{
            if (res.data === 'Valid'){
                axios.get(API_URL + `users/api/sendemail/?case=referral&to_email_address=${this.state.email}&username=${this.state.data.username}&referralid=${this.state.data.referral_id}`, config)
                .then(res =>{
                    alert(message)
                    this.props.history.push('/');
                }).catch(err => {
                    console.log(err.response)
                })
            }else{
                this.setState({error: true})
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
                                <FormattedMessage id='referral.enter_email' defaultMessage='Please enter the email account for your referral' />
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
                            <FormattedMessage id="balance.submit" defaultMessage='Submit' />   
                        </button>
                    </span>          

                </form>
                <button className="btn btn-secondary"> 
                    <NavLink to='/' style={{ textDecoration: 'none' }}><FormattedMessage id="profile.back" defaultMessage='Back' /></NavLink> 
                </button>
                {
                    this.state.error && <FormattedMessage id="referral.error" defaultMessage='You have reached the maximum referral number' />
                }

            </div>
        )
    }
}

export default injectIntl(Referral);