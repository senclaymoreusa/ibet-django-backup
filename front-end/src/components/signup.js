import React from 'react';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { authSignup, authCheckState, AUTH_RESULT_SUCCESS } from '../actions'
import axios from 'axios';
import { FormattedMessage } from 'react-intl';
import { config } from '../util_config';
import { errors } from './errors';
import Calendar from 'react-calendar';
import PasswordStrengthMeter from './PasswordStrengthMeter';
import IoEye from 'react-icons/lib/io/eye';
import { CountryDropdown } from 'react-country-region-selector';


const API_URL = process.env.REACT_APP_REST_API;


class Signup extends React.Component {

  constructor(props){
    super(props);

    this.state = {
      email_error: '',
      username_error: '',
      errorCode: '',
      password_error: '',
      hidden: true,
      phone_error: '',
  
      username: '',
      email: '',
      password1: '',
      password2: '',
      first_name: '',
      last_name: '',
      phone: '',
      date_of_birth: '',
      street_address_1: '',
      street_address_2: '',
      country: '',
      city: '',
      zipcode: '',
      state: '',
      date: new Date(),
      show_date: false
    };

    this.onInputChange_username         = this.onInputChange_username.bind(this);
    this.onInputChange_password1        = this.onInputChange_password1.bind(this)
    this.onInputChange_password2        = this.onInputChange_password2.bind(this)
    this.onInputChange_email            = this.onInputChange_email.bind(this);
    this.onInputChange_first_name       = this.onInputChange_first_name.bind(this);
    this.onInputChange_last_name        = this.onInputChange_last_name.bind(this);
    this.onInputChange_phone            = this.onInputChange_phone.bind(this);
    this.onInputChange_date_of_birth    = this.onInputChange_date_of_birth.bind(this);
    this.onInputChange_street_address_1 = this.onInputChange_street_address_1.bind(this);
    this.onInputChange_street_address_2 = this.onInputChange_street_address_2.bind(this);
    this.onInputChange_country          = this.onInputChange_country.bind(this);
    this.onInputChange_city             = this.onInputChange_city.bind(this);
    this.onInputChange_zipcode          = this.onInputChange_zipcode.bind(this);
    this.onInputChange_state            = this.onInputChange_state.bind(this);
    this.onFormSubmit                   = this.onFormSubmit.bind(this);
    this.onInputChange_date             = this.onInputChange_date.bind(this);
    this.toggleShow                     = this.toggleShow.bind(this);
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

  onInputChange_email(event){
    this.setState({email: event.target.value});
  }

  onInputChange_password1(event){
    this.setState({password1: event.target.value});
  }

  onInputChange_password2(event){
    this.setState({password2: event.target.value});
  }

  onInputChange_first_name(event){
    this.setState({first_name: event.target.value});
  }

  onInputChange_last_name(event){
    this.setState({last_name: event.target.value});
  }

  onInputChange_phone(event){
    this.setState({phone: event.target.value});
  }

  onInputChange_date_of_birth(event){
    this.setState({date_of_birth: event.target.value});
  }

  onInputChange_street_address_1(event){
    this.setState({street_address_1: event.target.value});
  }

  onInputChange_street_address_2(event){
    this.setState({street_address_2: event.target.value});
  }

  onInputChange_country(country){
    this.setState({country: country});
  }

  onInputChange_city(event){
    this.setState({city: event.target.value});
  }

  onInputChange_zipcode(event){
    this.setState({zipcode: event.target.value});
  }

  onInputChange_state(event){
    this.setState({state: event.target.value});
  }

  toggleShow() {
    this.setState({ hidden: !this.state.hidden });
  }

  onInputChange_date(date){
    var res = date.toString().split(" ");
    var month = res[1]
    var day = res[2]
    var year = res[3]
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    var months_to = [ '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    month = months_to[months.indexOf(month)]
    var result = month + '/' + day + '/' + year
    this.setState({date_of_birth: result})
  }

  onFormSubmit(event){
    event.preventDefault();

    this.setState({errorCode: ''})

    const referrer_id = this.props.location.pathname.slice(8)

    if (!this.state.username) {
      this.setState({ errorCode: errors.USERNAME_EMPTY_ERROR });
    } else if (!this.state.email) {
      this.setState({ errorCode: errors.EMAIL_EMPTY_ERROR });
    } else if (!this.state.password1 || !this.state.password2) {
      this.setState({ errorCode: errors.PASSWORD_EMPTY_ERROR });
    } else if (!this.state.first_name) {
      this.setState({ errorCode: errors.FIRST_NAME_EMPTY_ERROR });
    } else if (!this.state.last_name) {
      this.setState({ errorCode: errors.LAST_NAME_EMPTY_ERROR });
    } else if (!this.state.phone) {
      this.setState({ errorCode: errors.PHONE_EMPTY_ERROR });
    } else if (!this.state.date_of_birth) {
      this.setState({ errorCode: errors.DATEOFBIRTH_EMPTY_ERROR });
    } else if (!this.state.street_address_1) {
      this.setState({ errorCode: errors.STREET_EMPTY_ERROR });
    } else if (!this.state.city) {
      this.setState({ errorCode: errors.CITY_EMPTY_ERROR });
    } else if (!this.state.state) {
      this.setState({ errorCode: errors.STATE_EMPTY_ERROR });
    } else if (!this.state.country) {
      this.setState({ errorCode: errors.COUNTRY_EMPTY_ERROR });
    } else if (!this.state.zipcode){
      this.setState({ errorCode: errors.ZIPCODE_EMPTY_ERROR });
    } else {
        if (!referrer_id){
        this.props.authSignup(this.state.username, this.state.email, this.state.password1, this.state.password2, this.state.first_name, this.state.last_name, this.state.phone, this.state.date_of_birth, this.state.street_address_1, this.state.street_address_2, this.state.country, this.state.city, this.state.zipcode, this.state.state)
        .then((res) => {
          this.props.history.push('/activation');
          axios.post(API_URL + `users/api/activate/?email=${this.state.email}`)
          axios.get(API_URL + `users/api/sendemail/?case=signup&to_email_address=${this.state.email}&username=${this.state.username}&email=${this.state.email}`, config)
        }).catch(err => {
          // console.log(err.response);
          if ('username' in err.response.data) {
            this.setState({username_error: err.response.data.username[0]})
          } else {
            this.setState({username_error: ''})
          }

          if ('email' in err.response.data) {
            this.setState({email_error: err.response.data.email[0]})
          } else {
            this.setState({email_error: ''})
          }

          if ('phone' in err.response.data) {
            this.setState({phone_error: err.response.data.phone[0]})
          } else {
            this.setState({phone_error: ''})
          }

          if ('non_field_errors' in err.response.data) {
            this.setState({error: err.response.data.non_field_errors.slice(0)})
          }

          if ('password1' in err.response.data) {
            this.setState({password_error: err.response.data.password1[0]})
          }
        })
      }else{
          this.props.authSignup(this.state.username, this.state.email, this.state.password1, this.state.password2, this.state.first_name, this.state.last_name, this.state.phone, this.state.date_of_birth, this.state.street_address_1, this.state.street_address_2, this.state.country, this.state.city, this.state.zipcode, this.state.state)
          .then((res) => {
            this.props.history.push('/activation');
            axios.post(API_URL + `users/api/activate/?email=${this.state.email}`)
            axios.get(API_URL + `users/api/sendemail/?case=signup&to_email_address=${this.state.email}&username=${this.state.username}&email=${this.state.email}`, config)
            axios.get(API_URL + `users/api/referral/?referral_id=${referrer_id}&referred=${this.state.username}`, config)
        
        }).catch(err => {
            // console.log(err.response);
            if (err.response &&  'username' in err.response.data) {
              this.setState({username_error: err.response.data.username[0]})
            } else {
              this.setState({username_error: ''})
            }
    
            if (err.response && 'email' in err.response.data) {
              this.setState({email_error: err.response.data.email[0]})
            } else {
              this.setState({email_error: ''})
            }

            if (err.response && 'phone' in err.response.data) {
              this.setState({phone_error: err.response.data.phone[0]})
            } else {
              this.setState({phone_error: ''})
            }
    
            if (err.response && 'non_field_errors' in err.response.data) {
              this.setState({error: err.response.data.non_field_errors.slice(0)})
            }
    
            if (err.response && 'password1' in err.response.data) {
              this.setState({password_error: err.response.data.password1[0]})
            }
          })
      }
    }
  }

  render() {

    const showErrors = () => {
      if (this.state.errorCode === errors.USERNAME_EMPTY_ERROR) {
          return (
              <div style={{color: 'red'}}> 
                  <FormattedMessage id="sign.username_empty_error" defaultMessage='Username cannot be empty' /> 
              </div>
          );
      } else if (this.state.errorCode === errors.EMAIL_EMPTY_ERROR) {
          return (
              <div style={{color: 'red'}}> 
                  <FormattedMessage id="sign.email_empty_error" defaultMessage='Email cannot be empty' /> 
              </div>
          );
      } else if (this.state.errorCode === errors.PASSWORD_EMPTY_ERROR) {
        return (
            <div style={{color: 'red'}}> 
                <FormattedMessage id="sign.password_empty_error" defaultMessage='Password cannot be empty' /> 
            </div>
        );
      } else if (this.state.errorCode === errors.FIRST_NAME_EMPTY_ERROR) {
        return (
            <div style={{color: 'red'}}> 
                <FormattedMessage id="sign.firstName_empty_error" defaultMessage='First Name cannot be empty' /> 
            </div>
        );
      } else if (this.state.errorCode === errors.LAST_NAME_EMPTY_ERROR) {
        return (
            <div style={{color: 'red'}}> 
                <FormattedMessage id="sign.lastName_empty_error" defaultMessage='Last Name cannot be empty' /> 
            </div>
        );
      } else if (this.state.errorCode === errors.PHONE_EMPTY_ERROR) {
        return (
            <div style={{color: 'red'}}> 
                <FormattedMessage id="sign.phone_empty_error" defaultMessage='Phone cannot be empty' /> 
            </div>
        );
      } else if (this.state.errorCode === errors.DATEOFBIRTH_EMPTY_ERROR) {
        return (
            <div style={{color: 'red'}}> 
                <FormattedMessage id="sign.dob_empty_error" defaultMessage='Date Of Birth cannot be empty' /> 
            </div>
        );
      } else if (this.state.errorCode === errors.STREET_EMPTY_ERROR) {
        return (
            <div style={{color: 'red'}}> 
                <FormattedMessage id="sign.street_empty_error" defaultMessage='Street cannot be empty' /> 
            </div>
        );
      } else if (this.state.errorCode === errors.CITY_EMPTY_ERROR) {
        return (
            <div style={{color: 'red'}}> 
                <FormattedMessage id="sign.city_empty_error" defaultMessage='City cannot be empty' /> 
            </div>
        );
      } else if (this.state.errorCode === errors.STATE_EMPTY_ERROR) {
        return (
            <div style={{color: 'red'}}> 
                <FormattedMessage id="sign.state_empty_error" defaultMessage='State cannot be empty' /> 
            </div>
        );
      } else if (this.state.errorCode === errors.COUNTRY_EMPTY_ERROR) {
        return (
            <div style={{color: 'red'}}> 
                <FormattedMessage id="sign.country_empty_error" defaultMessage='Country cannot be empty' /> 
            </div>
        );
      } else if (this.state.errorCode === errors.ZIPCODE_EMPTY_ERROR) {
        return (
            <div style={{color: 'red'}}> 
                <FormattedMessage id="sign.zipcode_empty_error" defaultMessage='Zipcode cannot be empty' /> 
            </div>
        );
      } else if (this.state.username_error) {
        return (
            <div style={{color: 'red'}}> {this.state.username_error} </div>
        )
      } else if (this.state.email_error) {
        return (
            <div style={{color: 'red'}}> {this.state.email_error} </div>
        )
      } else if(this.state.phone_error){
        return (
            <div style={{color: 'red'}}> {this.state.phone_error} </div>
        )
      }else if (this.state.password_error) {
        return (
            <div style={{color: 'red'}}> {this.state.password_error} </div>
        )
      } else if (!this.state.username_error && !this.state.email_error && !this.state.password_error){
        return (
          <div style={{color: 'red'}}> {this.state.error} </div>
        )
      }
    }
    
    return (

      <div> 
        <form onSubmit={this.onFormSubmit} >

          <div>
            <label><b>
            <FormattedMessage id="signup.username" defaultMessage='Username: ' />  
            </b></label>
            <input
                placeholder="Wilson"
                className="form-control"
                value={this.state.username}
                onChange={this.onInputChange_username}
            />
          </div>

          <div>
            <label><b>
            <FormattedMessage id="signup.email" defaultMessage='Email: ' />    
            </b></label>
            <input
                placeholder="example@gmail.com"
                className="form-control"
                value={this.state.email}
                onChange={this.onInputChange_email}
            />
          </div>

          <div>
            <label><b>
            <FormattedMessage id="signup.password" defaultMessage='Password: ' />   
            </b></label>
            <input
                type = {this.state.hidden ? "password" : "text"}
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
            <FormattedMessage id="signup.confirm" defaultMessage='Confirm: ' />   
            </b></label>
            <input
                type = 'password'
                placeholder="password"
                className="form-control"
                value={this.state.password2}
                onChange={this.onInputChange_password2}
            />
          </div>

          <div>
            <label><b>
            <FormattedMessage id="signup.firstName" defaultMessage='First Name: ' />     
            </b></label>
            <input
                placeholder="Vicky"
                className="form-control"
                value={this.state.first_name}
                onChange={this.onInputChange_first_name}
            />
          </div>

          <div>
            <label><b>
            <FormattedMessage id="signup.lastName" defaultMessage='Last Name: ' />   
            </b></label>
            <input
                placeholder="Stephen"
                className="form-control"
                value={this.state.last_name}
                onChange={this.onInputChange_last_name}
            />
          </div>

          <div>
            <label><b>
            <FormattedMessage id="signup.phone" defaultMessage='Phone: ' />    
            </b></label>
            <input
                placeholder="9496541234"
                className="form-control"
                value={this.state.phone}
                onChange={this.onInputChange_phone}
            />
          </div>

          <div>
            <label><b>
            <FormattedMessage id="signup.dob" defaultMessage='Date of birth: ' />  
            </b></label>
            <input
                placeholder="mm/dd/yyyy"
                className="form-control"
                value={this.state.date_of_birth}
                onChange={this.onInputChange_date_of_birth}
            />
            <div onClick={() => {this.setState({show_date: !this.state.show_date})}} style={{color: 'blue'}}>
              <FormattedMessage id="sign.show_date" defaultMessage='Show date' />
            </div>
          </div>
         
          {
          this.state.show_date && <Calendar
            onChange={this.onInputChange_date}
            value={this.state.date}
          />
          }

          <div>
            <label><b>
            <FormattedMessage id="signup.street1" defaultMessage='Street Address 1: ' />    
            </b></label>
            <input
                placeholder="123 World Dr"
                className="form-control"
                value={this.state.street_address_1}
                onChange={this.onInputChange_street_address_1}
            />
          </div>     

          <div>
            <label><b>
            <FormattedMessage id="signup.street2" defaultMessage='Street Address 2: ' />      
            </b></label>
            <input
                placeholder="Suite 23"
                className="form-control"
                value={this.state.street_address_2}
                onChange={this.onInputChange_street_address_2}
            />
          </div>                

          <div>
            <label><b>
            <FormattedMessage id="signup.city" defaultMessage='City: ' />  
            </b></label>
            <input
                placeholder="Mountain View"
                className="form-control"
                value={this.state.city}
                onChange={this.onInputChange_city}
            />
          </div> 

          <div>
            <label><b>
            <FormattedMessage id="signup.state" defaultMessage='State: ' />  
            </b></label>
            <input
                placeholder="CA"
                className="form-control"
                value={this.state.state}
                onChange={this.onInputChange_state}
            />
          </div>           

          <div>
            <label><b>
            <FormattedMessage id="signup.country" defaultMessage='Country: ' />   
            </b></label>
            <CountryDropdown
              value={this.state.country}
              onChange={this.onInputChange_country} 
            />
          </div>           

          <div>
            <label><b>
            <FormattedMessage id="signup.zipcode" defaultMessage='Zipcode: ' />    
            </b></label>
            <input
                placeholder="92612"
                className="form-control"
                value={this.state.zipcode}
                onChange={this.onInputChange_zipcode}
            />
          </div> 

          <span className="input-group-btn">
              <button type="submit" className="btn btn-secondary"> 
              <FormattedMessage id="signup.submit" defaultMessage='Submit' />    
              </button>
          </span>          

        </form>

        <button> 
          <NavLink to='/' style={{ textDecoration: 'none', color: 'red' }}>
          <FormattedMessage id="signup.cancel" defaultMessage='Cancel' />
          </NavLink>
        </button>

        { showErrors() }

      </div>
    );
  }
}

const mapStateToProps = (state) => {
    return {
        loading: state.loading,
        error: state.error
    }
}

export default connect(mapStateToProps, {authSignup, authCheckState})(Signup);