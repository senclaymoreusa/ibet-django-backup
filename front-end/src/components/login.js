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


const API_URL = process.env.REACT_APP_REST_API;

var height = window.innerHeight
var width = window.innerWidth


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
      width: 300,
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
          button_clicked: 0,
          check: false,
          showPassword: false,

          live_check_username: false,
          live_check_password: false,
          button_disable: true,
          button_type: 'login-button-disable'
        };
    
        this.onInputChange_username         = this.onInputChange_username.bind(this);
        this.onInputChange_password         = this.onInputChange_password.bind(this)
        this.onFormSubmit                   = this.onFormSubmit.bind(this);
        this.toggleShow                     = this.toggleShow.bind(this);
        this.handle_one_click               = this.handle_one_click.bind(this);
    }


    
    handleClickShowPassword = () => {
        this.setState(state => ({ showPassword: !state.showPassword }));
    };

  async componentDidMount() {
    this.props.authCheckState()
    .then(res => {
      if (res === AUTH_RESULT_SUCCESS) {
        this.props.history.push('/'); 
      } 
    });

    const remember_check = localStorage.getItem('remember_check');
    if (remember_check){
        await this.setState({check: true})
    }

    const check = localStorage.getItem('one-click');
    if (check){
        const username = localStorage.getItem('username');
        const password = localStorage.getItem('password');
        localStorage.removeItem('one-click');
        localStorage.removeItem('username');
        localStorage.removeItem('password');
        this.setState({username: username, password: password, button_disable: false, button_type: 'login-button' })
    }else{
        const remember_check = localStorage.getItem('remember_check');
        if (remember_check){
            const username = localStorage.getItem('remember_username');
            const password = localStorage.getItem('remember_password');
            this.setState({username: username, password: password, button_disable: false, button_type: 'login-button' })
        }
    }
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
        this.setState({username: username, password: password, button_disable: false, button_type: 'login-button', check: false})

        localStorage.removeItem('remember_username');
        localStorage.removeItem('remember_password');
        localStorage.removeItem('remember_check');

        alert(message_username + username + '  ' + message_password + password)
    })
  }

  onInputChange_username(event){
    if(event.target.value && this.state.password){
        this.setState({button_disable: false, button_type: 'login-button'})
    }else{
        this.setState({button_disable: true, button_type: 'login-button-disable'})
    }
    this.setState({username: event.target.value});
  }

  onInputChange_password(event){
    if(event.target.value && this.state.username){
        this.setState({button_disable: false, button_type: 'login-button'})
    }else{
        this.setState({button_disable: true, button_type: 'login-button-disable'})
    }
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

  onInputChange_checkbox = async (event) => {
     await this.setState({check: !this.state.check})
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
            if (this.state.check){
                localStorage.setItem('remember_username', this.state.username);
                localStorage.setItem('remember_password', this.state.password);
                localStorage.setItem('remember_check', 'checked')
            }else{
                localStorage.removeItem('remember_username');
                localStorage.removeItem('remember_password');
                localStorage.removeItem('remember_check');
            }
            this.props.history.push('/');
        })
        .catch(err => {
            this.setState({errorCode: err});
        });
    }
  }

  render() {

    const { classes } = this.props;

    const { formatMessage } = this.props.intl;
    const remember_password = formatMessage({ id: "login.remember" });

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
            <TopNavbar />
            <div className='login-form '>

                <div className='title'> 
                    <FormattedMessage id="nav.login" defaultMessage='Login' />
                </div>

                <form onSubmit={this.onFormSubmit} >
                    
                    <FormattedMessage id="login.username" defaultMessage='Username: ' />
                    
                    <br/>
                    

                    <TextField
                        id="outlined-adornment-password"
                        className={classNames(classes.margin, classes.textField)}
                        variant="outlined"
                        type={'text'}
                        label="Username"
                        value={this.state.username}
                        onChange={this.onInputChange_username}
                    />


                    <br/>

                    <FormattedMessage id="login.password" defaultMessage='Password: ' />  
    
                    <br/>


                    <TextField
                        id="outlined-adornment-password"
                        className={classNames(classes.margin, classes.textField)}
                        variant="outlined"
                        type={this.state.showPassword ? 'text' : 'password'}
                        label="Password"
                        value={this.state.password}
                        onChange={this.onInputChange_password}
                        InputProps={{
                            endAdornment: (
                            <InputAdornment position="end">
                                <IconButton
                                aria-label="Toggle password visibility"
                                onClick={this.handleClickShowPassword}
                                >
                                {this.state.showPassword ? <VisibilityOff /> : <Visibility />}
                                </IconButton>
                            </InputAdornment>
                            ),
                        }}
                    />
    
                    <br/>

                    <FormControlLabel
                        control={
                            <Checkbox
                            checked={this.state.check}
                            onChange={this.onInputChange_checkbox}
                            value="checkedA"
                            />
                        }
                        label = {remember_password}
                    />

                    <br />

                    <Button 
                        variant="contained"
                        color="primary"
                        disabled = {this.state.button_disable} 
                        className={this.state.button_type} 
                        type="submit" > 
                        <FormattedMessage id="login.login" defaultMessage='Login' />
                    </Button>

                </form>


                <br/>

                <div> 
                    <NavLink to='/forget_password' style={{ textDecoration: 'none', color: 'blue' }}>
                        <FormattedMessage id="login.forget_password" defaultMessage='Forgot Password?' /> 
                    </NavLink>
                </div>

                <br/>

                <div> 
                    <NavLink to='/signup' style={{ textDecoration: 'none', color: 'blue' }}>
                        <FormattedMessage id="login.notauser" defaultMessage='Not a member? Signup for free' /> 
                    </NavLink>
                </div>

                <br/>

                <div> 
                    <FormattedMessage id="login.one-click" defaultMessage='Or try one click signup' />
                </div>

                <br/>

                <div> 
                    <Button  
                        onClick={this.handle_one_click}
                        variant="contained"
                        color="primary"
                        className={this.state.button_type}
                    >
                        <FormattedMessage id="login.signup" defaultMessage='Signup' />
                    </Button>
                </div>


                <br/>

                <div>
                    <FormattedMessage id="login.option" defaultMessage='Other login options' />
                </div>

                <br />

                <div> 
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
                </div>

                <br/>

                <br/>
                {
                    showErrors()
                }
        </div>
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

export default withStyles(styles)(injectIntl(connect(mapStateToProps, {authLogin, authCheckState, FacebookSignup, FacebookauthLogin})(Login)));