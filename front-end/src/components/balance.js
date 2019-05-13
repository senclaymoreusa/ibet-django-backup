import React, { Component } from 'react';
import { FormattedMessage, injectIntl } from 'react-intl';
import { NavLink} from 'react-router-dom';
import axios from 'axios';
import { config } from '../util_config';
import { connect } from 'react-redux';

const API_URL = process.env.REACT_APP_REST_API;

class Balance extends Component {
    constructor(props){
        super(props);
    
        this.state = {
          balance: '',
          error: false,
          data: '',
          type: '',
        };

        this.onInputChange_balance          = this.onInputChange_balance.bind(this);
        this.onFormSubmit                   = this.onFormSubmit.bind(this);
    }
    
    componentDidMount() {
        const token = localStorage.getItem('token');
        config.headers["Authorization"] = `Token ${token}`;

        axios.get(API_URL + 'users/api/user/', config)
          .then(res => {
            this.setState({data: res.data});
          })
        const { type } = this.props.match.params;
        this.setState({type: type});

    }

    onInputChange_balance(event){
        this.setState({balance: event.target.value}); 
    }

    onFormSubmit(event){
        const { formatMessage } = this.props.intl;
        let message = '';
        if (this.state.type === 'add') {
            message = formatMessage({ id: "balance.confirm" });
        } else {
            message = formatMessage({ id: "balance.withdrawconfirm" });
        }
        
        event.preventDefault();
        if (window.confirm( message + this.state.balance)){
            
            const body = JSON.stringify({
                type : this.state.type,
                username: this.state.data.username,
                balance: this.state.balance
            });
            axios.post(API_URL + `users/api/addorwithdrawbalance/`, body, config)
            .then(res => {
                if (res.data === 'Failed'){
                    this.setState({error: true});
                } else if (res.data === 'The balance is not enough') {
                    alert("cannot withdraw this amount")
                } else {
                    this.props.history.push("/profile");
                }
            });
        }
    }

    render(){
        return (
            <div>
                <form onSubmit={this.onFormSubmit} >
                    <div>
                        <div>
                            {this.state.type === 'add' ? 
                            <label><b>
                                <FormattedMessage id='balance.enter_balance' defaultMessage='Please enter the amount you want to add to your account' />
                            </b></label>
                            :
                            <label><b>
                                <FormattedMessage id='balance.withdraw_balance' defaultMessage='Please enter the amount you want to withdraw from your account' />
                            </b></label>
                            }
                            
                        </div>
                        <input
                            placeholder="$50.00"
                            className="form-control"
                            value={this.state.balance}
                            onChange={this.onInputChange_balance}
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
                <br/>
                {
                    this.state.error && <div style = {{color: 'red'}}> <FormattedMessage  id="balance.error" defaultMessage='The balance you entered is not valid' /> </div>
                }
            </div>
        )
    }
}

const mapStateToProps = (state) => {
    return {
        language: state.language.lang,
    }
}

export default injectIntl(connect(mapStateToProps)(Balance));