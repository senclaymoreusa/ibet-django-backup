import React, { Component } from 'react';
import axios from 'axios';
import { errors } from './errors';
import { withRouter } from 'react-router-dom';
import { FormattedMessage } from 'react-intl';
import { config } from '../util_config';
import PasswordStrengthMeter from './PasswordStrengthMeter';
import IoEye from 'react-icons/lib/io/eye';


const API_URL = process.env.REACT_APP_REST_API;

class Reset_Password extends Component {

    constructor(props){
        super(props);

        this.state = {
           show_page: true,
           password1: '',
           password2: '',
           error_message: '',
           errorCode: '',
           hidden: true
        }

        this.onInputChange_password1  = this.onInputChange_password1.bind(this);
        this.onInputChange_password2  = this.onInputChange_password2.bind(this);
        this.onFormSubmit             = this.onFormSubmit.bind(this);
        this.toggleShow               = this.toggleShow.bind(this);
    }

    componentDidMount() {

        const body = {
            token: this.props.location.pathname.slice(16)
        }

        axios.post(API_URL + 'users/api/reset-password/verify-token/', body, config)
        .then(res => {
          // does nothing
        }).catch(err => {
          this.setState({show_page: false})
        })
    }

    onInputChange_password1(event){
        this.setState({password1: event.target.value});
    }

    onInputChange_password2(event){
        this.setState({password2: event.target.value});
    }

    toggleShow() {
        this.setState({ hidden: !this.state.hidden });
      }

    onFormSubmit(event){
        event.preventDefault();

        const body = {
            token: this.props.location.pathname.slice(16),
            password: this.state.password1
        }
        
        if (this.state.password1 !== this.state.password2) {
            this.setState({ errorCode: errors.PASSWORD_NOT_MATCH });
        } else if ( this.state.password1.length < 8){ 
            this.setState({ errorCode: errors.PASSWORD_NOT_VALID });
        } else {
            this.setState({ errorCode: '' });
            axios.post(API_URL + 'users/api/reset-password/confirm/', body, config)
            .then(res => {
                this.props.history.push("/reset_password_done")
            })
        }
    }

    render(){

        const showErrors = () => {
            if (this.state.errorCode === errors.PASSWORD_NOT_MATCH) {
                return (
                    <div style={{color: 'red'}}> 
                        <FormattedMessage id="reset_password.password_not_match" defaultMessage='Password not match' /> 
                    </div>
                );
            } else if (this.state.errorCode === errors.PASSWORD_NOT_VALID) {
                return (
                    <div style={{color: 'red'}}> 
                        <FormattedMessage id="reset_password.password_not_valid" defaultMessage='Password not valid' /> 
                    </div>
                );
            } 
        }

        return (
            <div> 
                {
                    this.state.show_page ?
                    <div>
                        <div>
                        <FormattedMessage id="reset_password.change_password" defaultMessage='Change your password' />      
                        </div>
                        <form onSubmit={this.onFormSubmit} >

                        <div> 
                            <label><b>
                            <FormattedMessage id="reset_password.password" defaultMessage='Password: ' /> 
                            </b></label>
                            <input
                                type={this.state.hidden ? "password" : "text"}
                                placeholder="password"
                                className="form-control"
                                value={this.state.password1}
                                onChange={this.onInputChange_password1}
                            />

                            <span style = {{position: 'relative',  left: '-25px'}} onMouseDown={this.toggleShow} onMouseUp={this.toggleShow}> <IoEye /> </span>

                            {
                              this.state.password1 && <PasswordStrengthMeter password={this.state.password1} />
                            }
                            
                        </div>

                        <div>
                            <label><b>
                            <FormattedMessage id="reset_password.confirm_password" defaultMessage='Confirm Password: ' />     
                            </b></label>
                            <input
                                type="password"
                                placeholder="password"
                                className="form-control"
                                value={this.state.password2}
                                onChange={this.onInputChange_password2}
                            />
                        </div>
                            <span className="input-group-btn">
                                <button type="submit" className="btn btn-secondary"> 
                                <FormattedMessage id="reset_password.confirm" defaultMessage='Confirm' />      
                                </button>
                            </span>
                        </form>
                    </div>
                    : 
                    <div> <FormattedMessage id="reset_password.page_not_valid" defaultMessage='You have successfully reset your password' /> </div>
                }

                {
                    // <div style={{color: 'red'}}> {this.state.error_message} </div>
                    showErrors()
                }

            </div>
        )
    }
}

export default withRouter(Reset_Password);