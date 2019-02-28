import React from 'react';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { authLogin, authCheckState, AUTH_RESULT_SUCCESS } from '../actions'
import { messages } from './messages';

class Login extends React.Component {

    constructor(props){
        super(props);
    
        this.state = {
          error: '',
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
        this.setState({error: messages.USERNAME_EMPTY_ERROR})
    }else if(!this.state.password){
        this.setState({error: messages.EMAIL_EMPTY_ERROR})
    }else{
        this.props.authLogin(this.state.username, this.state.password)
        .then(() => {
            this.props.history.push('/');
        })
        .catch(err => {
            this.setState({error: messages.LOGIN_ERROR})
        });
    }
  }

  render() {
    
    return (
        <div>
        <form onSubmit={this.onFormSubmit} >

            <div>
            <label><b>Username:</b></label>
            <input
                placeholder="claymore"
                className="form-control"
                value={this.state.username}
                onChange={this.onInputChange_username}
            />
            </div>

            <div>
            <label><b>Password:</b></label>
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
                    Log in 
                </button>
            </span> 
            or         
            <NavLink to='/signup' style={{ textDecoration: 'none', color: 'blue' }}>
                {' Sign up'}
            </NavLink>
            <br/>
            <NavLink to='/forget_password' style={{ textDecoration: 'none', color: 'blue' }}>
                Forget password?
            </NavLink>
        </form>

        <button> 
            <NavLink to='/' style={{ textDecoration: 'none', color: 'red' }}>
             Back
            </NavLink>
        </button>
        <br/>
        {
            <div style={{color: 'red'}}> {this.state.error} </div>
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