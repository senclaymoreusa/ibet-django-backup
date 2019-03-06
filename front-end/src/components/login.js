import React from 'react';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { FormattedMessage } from 'react-intl';
import { errors } from './errors';
import { authLogin, authCheckState, AUTH_RESULT_SUCCESS } from '../actions'

class Login extends React.Component {

    constructor(props){
        super(props);
    
        this.state = {
          errorCode: '',
          username: '',
          password: '',
        };
    
        this.onInputChange_username         = this.onInputChange_username.bind(this);
        this.onInputChange_password         = this.onInputChange_password.bind(this)
        this.onFormSubmit                   = this.onFormSubmit.bind(this);
    }

  componentDidMount() {
    this.props.authCheckState()
    .then(res => {
      if (res === AUTH_RESULT_SUCCESS) {
        this.props.history.push('/'); 
      } 
    });
  }

  onInputChange_username(event){
    this.setState({username: event.target.value});
  }

  onInputChange_password(event){
    this.setState({password: event.target.value});
  }

  onFormSubmit(event){
    event.preventDefault();

    if (!this.state.username){
        this.setState({ errorCode: errors.USERNAME_EMPTY_ERROR });
    }else if(!this.state.password){
        this.setState({ errorCode: errors.PASSWORD_EMPTY_ERROR });
    }else{
        this.props.authLogin(this.state.username, this.state.password)
        .then(() => {
            this.props.history.push('/');
        })
        .catch(err => {
            this.setState({errorCode: err})
        });
    }
  }

  render() {


    const showErrors = () => {
      if (this.state.errorCode === errors.USERNAME_EMPTY_ERROR) {
          return (
              <div style={{color: 'red'}}> 
                  <FormattedMessage id="login.username_empty_error" defaultMessage='Username cannot be empty' /> 
              </div>
          );
      } else if (this.state.errorCode === errors.PASSWORD_EMPTY_ERROR) {
          return (
              <div style={{color: 'red'}}> 
                  <FormattedMessage id="login.password_empty_error" defaultMessage='Password cannot be empty' /> 
              </div>
          );
      } else {
        return (
            <div style={{color: 'red'}}> {this.state.errorCode} </div>
        )
      }
    }
    
    return (
        <div>
        <form onSubmit={this.onFormSubmit} >

            <div>
            <label><b>
            <FormattedMessage id="login.username" defaultMessage='Username: ' />
            </b></label>
            <input
                placeholder="claymore"
                className="form-control"
                value={this.state.username}
                onChange={this.onInputChange_username}
            />
            </div>

            <div>
            <label><b>
            <FormattedMessage id="login.password" defaultMessage='Password: ' />  
            </b></label>
            <input
                type = 'password'
                placeholder="password"
                className="form-control"
                value={this.state.password}
                onChange={this.onInputChange_password}
            />
            </div>

            <span className="input-group-btn">
                <button type="submit" className="btn btn-secondary"> 
                <FormattedMessage id="login.login" defaultMessage='Login' />
                </button>
            </span> 
            <FormattedMessage id="login.or" defaultMessage='Or' />        
            <NavLink to='/signup' style={{ textDecoration: 'none', color: 'blue' }}>
                <FormattedMessage id="login.signup" defaultMessage='Signup' />
            </NavLink>
            <br/>
            <NavLink to='/forget_password' style={{ textDecoration: 'none', color: 'blue' }}>
                <FormattedMessage id="login.forget_password" defaultMessage='Forget password' /> 
            </NavLink>
        </form>

        <button> 
            <NavLink to='/' style={{ textDecoration: 'none', color: 'red' }}>
            <FormattedMessage id="login.back" defaultMessage='Back' /> 
            </NavLink>
        </button>
        <br/>
        {
            showErrors()
        }
    </div>
    );
  }
}

const mapStateToProps = (state) => {
    return {
        loading: state.auth.loading,
        error: state.auth.error,
    }
}

export default connect(mapStateToProps, {authLogin, authCheckState})(Login);