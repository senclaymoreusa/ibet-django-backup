import React, { Component } from 'react';
import axios from 'axios';
import { messages } from './messages';
import { withRouter } from 'react-router-dom';

const API_URL = process.env.REACT_APP_REST_API

class Reset_Password extends Component {

    constructor(props){
        super(props);

        this.state = {
           show_page: true,
           password1: '',
           password2: '',
           error_message: ''
        }

        this.onInputChange_password1  = this.onInputChange_password1.bind(this);
        this.onInputChange_password2  = this.onInputChange_password2.bind(this);
        this.onFormSubmit             = this.onFormSubmit.bind(this);
    }

    componentDidMount() {
        const config = {
            headers: {
              "Content-Type": "application/json"
            }
        };

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

    onFormSubmit(event){
        event.preventDefault();
        
        const config = {
            headers: {
              "Content-Type": "application/json"
            }
        };

        const body = {
            token: this.props.location.pathname.slice(16),
            password: this.state.password1
        }
        
        if (this.state.password1 !== this.state.password2){
            this.setState({error_message: messages.PASSWORD_NOT_MATCH})
        }else if( this.state.password1.length < 8){
            this.setState({error_message: messages.PASSWORD_NOT_VALID})
        }else{
            this.setState({error_message: ''})
            axios.post(API_URL + 'users/api/reset-password/confirm/', body, config)
            .then(res => {
                this.props.history.push("/reset_password_done")
            })
        }
    }

    render(){
        return (
            <div> 
                {
                    this.state.show_page ?
                    <div>
                        <div> Change your password </div>
                        <form onSubmit={this.onFormSubmit} >

                        <div> 
                            <label><b>Password:</b></label>
                            <input
                                type="password"
                                placeholder="password"
                                className="form-control"
                                value={this.state.password1}
                                onChange={this.onInputChange_password1}
                            />
                        </div>

                        <div>
                            <label><b>Confirm Password:</b></label>
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
                                    Confirm
                                </button>
                            </span>
                        </form>
                    </div>
                    : 
                    <div> {messages.PAGE_NOT_VALID} </div>
                }

                {
                    <div style={{color: 'red'}}> {this.state.error_message} </div>
                }

            </div>
        )
    }
}

export default withRouter(Reset_Password);