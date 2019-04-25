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
          error: false,
          email_exist_error: false,
          button_disable: true,
          email_valid_error: false
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
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        if (!event.target.value.match(re)  ){
            this.setState({email_valid_error: true, button_disable: true});
        }else if(event.target.value === this.state.data.email){
            this.setState({email_exist_error: true, button_disable: true});
        }else{
            this.setState({email_valid_error: false, email_exist_error: false, button_disable: false});
        }
        this.setState({ email: event.target.value });
    }

    onFormSubmit(event){
        const { formatMessage } = this.props.intl;
        const message = formatMessage({ id: 'referral.user' });

        event.preventDefault();
        axios.get(API_URL + `users/api/checkreferral?referral_id=${this.state.data.referral_id}&email=${this.state.email}`, config)
        .then(res =>{
            if (res.data === 'Duplicate'){
                this.setState({email_exist_error: true})
            }else if (res.data === 'Valid'){
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
                        <button disabled = {this.state.button_disable} type="submit" className="btn btn-secondary"> 
                            <FormattedMessage id="balance.submit" defaultMessage='Submit' />   
                        </button>
                    </span>          

                </form>

                <button className="btn btn-secondary"> 
                    <NavLink to='/' style={{ textDecoration: 'none' }}><FormattedMessage id="profile.back" defaultMessage='Back' /></NavLink> 
                </button>

                <br/>

                {
                    this.state.error && <FormattedMessage id="referral.error" defaultMessage='You have reached the maximum referral number' />
                }

                {
                    this.state.email_valid_error && <div style={{color: 'red'}}> <FormattedMessage id="referral.email_valid" defaultMessage='Please enter a valid email address' /> </div>
                }

                {
                    this.state.email_exist_error && <div style={{color: 'red'}}> <FormattedMessage id="referral.email_exist" defaultMessage='This email has already been registerd' /> </div>
                }

            </div>
        )
    }
}

export default injectIntl(Referral);