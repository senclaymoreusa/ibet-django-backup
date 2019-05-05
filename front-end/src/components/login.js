import React from 'react';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { FormattedMessage, injectIntl} from 'react-intl';
import { errors } from './errors';
import { authLogin, authCheckState, AUTH_RESULT_SUCCESS, FacebookSignup, FacebookauthLogin } from '../actions';
import IoEye from 'react-icons/lib/io/eye';
import FacebookLogin from "react-facebook-login";
import axios from 'axios';
import IoSocialFacebook from 'react-icons/lib/io/social-facebook';
import '../css/login.css';


const API_URL = process.env.REACT_APP_REST_API;

var height = window.innerHeight
var width = window.innerWidth

export class Login extends React.Component {

    constructor(props){
        super(props);
    
        this.state = {
          errorCode: '',
          username: '',
          password: '',
          hidden: true,

          name: '',
          email: '',
          button_clicked: 0
        };
    
        this.onInputChange_username         = this.onInputChange_username.bind(this);
        this.onInputChange_password         = this.onInputChange_password.bind(this)
        this.onFormSubmit                   = this.onFormSubmit.bind(this);
        this.toggleShow                     = this.toggleShow.bind(this);
        this.handle_one_click               = this.handle_one_click.bind(this);
    }

  componentDidMount() {
    this.props.authCheckState()
    .then(res => {
      if (res === AUTH_RESULT_SUCCESS) {
        this.props.history.push('/'); 
      } 
    });
  }

  handle_one_click(){
    axios.post(API_URL + 'users/api/oneclicksignup/')
    .then(res => {
        const { formatMessage } = this.props.intl;
        const message_username = formatMessage({ id: "login.username" });

        const message_password = formatMessage({ id: "login.password" });

        var temp = res.data.split('-')
        var username = temp[0]
        var password = temp[1]
        alert(message_username + username + '  ' + message_password + password)
    })
  }

  onInputChange_username(event){
    this.setState({username: event.target.value});
  }

  onInputChange_password(event){
    this.setState({password: event.target.value});
  }

  toggleShow() {
    this.setState({ hidden: !this.state.hidden });
  }

  componentClicked = () => {
    this.setState({button_clicked: 1})
    var username = this.state.name
    var email = this.state.email
    console.log(username, email)

    this.props.FacebookauthLogin(username, email)
    .then(res => {
        this.props.history.push('/');
    }).catch(err => {
        this.props.FacebookSignup(username, email)
        .then(res => {
            this.props.FacebookauthLogin(username, email)
            .then(res => {
                this.props.history.push('/');
            })
            .catch(err => {
            })
        })
        .catch(err => {
        })
    })
  }

  FacebookFailed = () => {
      console.log('Facebook Login cancelled')
  }

  responseFacebook = (response) => {
    //console.log(response);
    
    localStorage.setItem('facebook', true)

    var facebookObj = {
        userID:  response.userID,
        name:    response.name,
        email:   response.email,
        picture: response.picture.data.url
    }

    this.setState({
      name:  response.name,
      email: response.email
    })

    localStorage.setItem('facebookObj', JSON.stringify(facebookObj));

    var username = this.state.name
    var email = this.state.email
    
    if (this.state.button_clicked === 1){
        this.props.FacebookauthLogin(username, email)
        .then(res => {
            this.props.history.push('/');
        }).catch(err => {
            this.props.FacebookSignup(username, email)
            .then(res => {
                this.props.FacebookauthLogin(username, email)
                .then(res => {
                    this.props.history.push('/');
                })
                .catch(err => {
                })
            })
            .catch(err => {
            })
        })
    }
  };

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
            this.setState({errorCode: err});
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
        <div className='login-form '>

            <div className='title'> 
                <FormattedMessage id="nav.login" defaultMessage='Login' />
            </div>

            <form onSubmit={this.onFormSubmit} >
                
                <FormattedMessage id="login.username" defaultMessage='Username: ' />
                
                <br/>

                <input
                    placeholder="claymore"
                    className="form-control"
                    value={this.state.username}
                    onChange={this.onInputChange_username}
                />

                <br/>

                <FormattedMessage id="login.password" defaultMessage='Password: ' />  
 
                <br/>

                <input
                    
                    type = {this.state.hidden ? "password" : "text"}
                    placeholder="password"
                    className="form-control"
                    value={this.state.password}
                    onChange={this.onInputChange_password}
                />


                <span style ={{position: 'relative',  left: '-25px'}} onMouseDown={this.toggleShow} onMouseUp={this.toggleShow}> <IoEye /> </span>
 
                <br/>

                <button className="login-button" type="submit" > 
                    <FormattedMessage id="login.login" defaultMessage='Login' />
                </button>
                
                <br />

                <div className='or'> 
                    <FormattedMessage id="login.or" defaultMessage='Or' /> 
                </div>

       

                <button className="submit-button" onClick={ () => {this.props.history.push('/signup/')}}>
                    <FormattedMessage id="login.signup" defaultMessage='Signup' />
                </button>

                <br/>


                <div className='forget'> 
                    <NavLink to='/forget_password' style={{ textDecoration: 'none', color: 'blue' }}>
                        <FormattedMessage id="login.forget_password" defaultMessage='Forgot Password?' /> 
                    </NavLink>
                </div>


            </form>

            <FormattedMessage id="login.one-click" defaultMessage='Or try one click signup' />

            <button style={{marginLeft: width * 0.02}} onClick={this.handle_one_click}>
                <FormattedMessage id="login.signup" defaultMessage='Signup' />
            </button>


            <br/>

            <div style={{marginLeft: width * 0.05, marginTop: height * 0.01}}>
                <FormattedMessage id="login.option" defaultMessage='Or login with' />
            </div>

            <FacebookLogin
                appId="236001567251034"
                size = 'small'
                textButton=""
                fields="name, email, picture"
                onClick={this.componentClicked}
                callback={this.responseFacebook}
                onFailure={this.FacebookFailed}
                icon ={ 
                    <div style={{fontSize: '25px'}}> 
                        <IoSocialFacebook />
                    </div>
                }
            />

            <br/>

            <button className="back" onClick={ () => {this.props.history.push('/')}}>
                <FormattedMessage id="login.back" defaultMessage='Back' />
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
    const { token } = state.auth;
    return {
        isAuthenticated: token !== null && token !== undefined,
        loading: state.auth.loading,
        error: state.auth.error,
    }
}

export default injectIntl(connect(mapStateToProps, {authLogin, authCheckState, FacebookSignup, FacebookauthLogin})(Login));