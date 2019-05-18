import React, { Component } from 'react';
import { FormattedMessage, injectIntl } from 'react-intl';
import { NavLink } from 'react-router-dom';
import { config } from '../util_config';
import axios from 'axios';


// Material design
import { withStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import InputAdornment from '@material-ui/core/InputAdornment';
import IconButton from '@material-ui/core/IconButton';
import Visibility from '@material-ui/icons/Visibility';
import VisibilityOff from '@material-ui/icons/VisibilityOff';
import Button from '@material-ui/core/Button';
import blue from '@material-ui/core/colors/blue';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';
import classNames from 'classnames';

import TopNavbar from "./top_navbar";


import '../css/email_sent.css';
import Axios from 'axios';

const API_URL = process.env.REACT_APP_REST_API;


const styles = theme => ({
    root: {
      display: 'flex',
      flexWrap: 'wrap',
    },

    margin: {
      margin: 'auto',
    },

    textField: {
      flexBasis: 200,
      width: 50,
      height: 50
    },

    cssRoot: {
        color: theme.palette.getContrastText(blue[300]),
        backgroundColor: blue[300],
        '&:hover': {
          backgroundColor: blue[800],
        },
      },
  });


class Email_Sent extends Component {

    constructor(props){
        super(props);

        this.state = {
           code_1: '',
           code_2: '',
           code_3: '',
           code_4: '',
           button_disable: true,
           error: false
        }

        this.handle_code_1 = this.handle_code_1.bind(this);
        this.handle_code_2 = this.handle_code_2.bind(this);
        this.handle_code_3 = this.handle_code_3.bind(this);
        this.handle_code_4 = this.handle_code_4.bind(this);
        this.check_valid   = this.check_valid.bind(this);
        this.onFormSubmit  = this.onFormSubmit.bind(this);
    }

    async handle_code_1(event){
        if(!event.target.value || (event.target.value.match(/^[0-9]+$/) && event.target.value.length < 2)){
            await this.setState({code_1: event.target.value})
        }
        this.check_valid();
    }

    async handle_code_2(event){
        if(!event.target.value ||  (event.target.value.match(/^[0-9]+$/) && event.target.value.length < 2)){
           await  this.setState({code_2: event.target.value})
        }
        this.check_valid();
    }

    async handle_code_3(event){
        if(!event.target.value ||  (event.target.value.match(/^[0-9]+$/) && event.target.value.length < 2)){
            await this.setState({code_3: event.target.value})
        }
        this.check_valid();
    }

    async handle_code_4(event){
        if(!event.target.value ||  (event.target.value.match(/^[0-9]+$/) && event.target.value.length < 2)){
            await this.setState({code_4: event.target.value})
        }
        this.check_valid();
    }

    check_valid(){
        if (this.state.code_1 && this.state.code_2 && this.state.code_3 && this.state.code_4){
            this.setState({button_disable: false})
        }else{
            this.setState({button_disable: true})
        }
    }

    onFormSubmit(event){
        event.preventDefault();
        
        const code = this.state.code_1 + this.state.code_2 + this.state.code_3  + this.state.code_4 

        axios.post(API_URL + `users/api/verifyresetpasswordcode/`,{
            email: this.props.match.params.email,
            code: code
        }, config)
        .then(res => {
          if (res.data === 'Success'){
               this.props.history.push(`/reset_password/${this.props.match.params.email}`)
          }else{
               this.setState({error: true})
          }
        })
    }

    render(){

        const { email } = this.props.match.params;

        const { classes } = this.props;

        return (
            <div> 

                <TopNavbar />

                <div className='email-sent-form '> 
                    <div>
                        <b> 
                            <FormattedMessage id="email_sent.topmessage" defaultMessage='We sent to a code to reset you password' />
                        </b>
                    </div>

                    <br/>

                    <div> 
                        <FormattedMessage id="email_sent.sentto" defaultMessage='Sent to' />
                    </div>
                    
                    <div> { email } </div>
                    
                    <br/>

                    <div> 
                        <FormattedMessage id="email_sent.resend" defaultMessage="Try resending the email if you haven't received in five minutes" />
                    </div>
                    
                    <br/>
                    
                    <div> 
                        <FormattedMessage id="email_sent.verify" defaultMessage='Verification Code' />
                    </div>
                    
                    <br/>

                    <form onSubmit={this.onFormSubmit} >

                        <TextField
                            id="outlined-adornment-password"
                            className={classNames(classes.margin, classes.textField)}
                            variant="outlined"
                            type={'text'}
                            value={this.state.code_1}
                            onChange={this.handle_code_1}
                        />

                        <TextField
                            id="outlined-adornment-password"
                            className={classNames(classes.margin, classes.textField)}
                            variant="outlined"
                            type={'text'}
                            value={this.state.code_2}
                            onChange={this.handle_code_2}
                        />

                        <TextField
                            id="outlined-adornment-password"
                            className={classNames(classes.margin, classes.textField)}
                            variant="outlined"
                            type={'text'}
                            value={this.state.code_3}
                            onChange={this.handle_code_3}
                        />

                        <TextField
                            id="outlined-adornment-password"
                            className={classNames(classes.margin, classes.textField)}
                            variant="outlined"
                            type={'text'}
                            value={this.state.code_4}
                            onChange={this.handle_code_4}
                        />

                        <br />
                        <br />

                        <Button 
                            variant="contained"
                            color="primary"
                            disabled = {this.state.button_disable} 
                            type="submit" 
                        > 
                    
                            <FormattedMessage id="forget_password.confirm" defaultMessage='Confirm' />
                        </Button>
                    </form>

                    <br/>

                    <div 
                    className='pointer'
                    style={{
                        color: 'blue',
                    }}
                    onClick={() => {
                        axios.post(API_URL + `users/api/generatepasswordcode/`, {email: email},config)
                        .then(res => {
                            if (res.data === 'Success'){
                                axios.post(API_URL + `users/api/sendresetpasswordcode/`,{email: email}, config)
                                .then(res => {
                                    const { formatMessage } = this.props.intl;
                                    const message = formatMessage({ id: "email_sent.resendsuccess" });
                                    alert(message)
                                })
                            }
                        })
                    }}>
                        <FormattedMessage id="reset_password.resend" defaultMessage='Resend email' />
                    </div>

                    <div style={{color: 'red'}}>
                        {
                            this.state.error && <FormattedMessage id="email_sent.error" defaultMessage='The verification code is not correct or it is outdated, try resending email' />
                        }
                    </div>
                </div>
            </div>
        )
    }
}

export default withStyles(styles)(injectIntl(Email_Sent));