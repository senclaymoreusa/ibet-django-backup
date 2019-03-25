import React, { Component } from 'react';
import { FormattedMessage } from 'react-intl';
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
          data: ''
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
    }

    onInputChange_balance(event){
        this.setState({balance: event.target.value}); 
    }

    onFormSubmit(event){
        event.preventDefault();
        var message;
        // This part is not available for FormattedMessage to translate so I have to translate it manually 
        if (this.props.language === 'en'){
            message = 'The amount you want to add to your balance is $ ';
        }else if(this.props.language === 'zh'){
            message = '您要加入的资金数量是 $ ';
        }else{
            message = 'Le montant que vous souhaitez rejoindre est de $'
        }
        if (window.confirm( message + this.state.balance)){
            axios.post(API_URL + `users/api/addbalance/?username=${this.state.data.username}&balance=${this.state.balance}`)
            .then(res => {
                if (res.data === 'Failed'){
                    this.setState({error: true});
                }else{
                    this.props.history.push("/profile");
                }
            })
        }
    }

    render(){
        return (
            <div>
                <form onSubmit={this.onFormSubmit} >
                    <div>
                        <div>
                            <label><b>
                                <FormattedMessage id='balance.enter_balance' defaultMessage='Please enter the amount you want to add to your account' />
                            </b></label>
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

export default connect(mapStateToProps)(Balance);