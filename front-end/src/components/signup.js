import React from 'react';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { authSignup, authCheckState, AUTH_RESULT_SUCCESS } from '../actions'
import axios from 'axios';
import { FormattedMessage, injectIntl } from 'react-intl';
import { config } from '../util_config';
import { errors } from './errors';
import Calendar from 'react-calendar';
import PasswordStrengthMeter from './PasswordStrengthMeter';
import IoEye from 'react-icons/lib/io/eye';
import Dropdown from 'react-dropdown'
import 'react-dropdown/style.css'
import { CountryDropdown } from 'react-country-region-selector';
import 'react-phone-number-input/style.css'
import PhoneInput from 'react-phone-number-input'


const options = ['Male', 'Female']

const contact = ['Email', 'SMS', 'OMS', 'Push Notification']

const API_URL = process.env.REACT_APP_REST_API;

var height = window.innerHeight
var width = window.innerWidth

class Signup extends React.Component {

  constructor(props){
    super(props);

    this.state = {
      email_error: '',
      username_error: '',
      errorCode: '',
      password_error: '',
      hidden: true,

      button_color: 'grey',
      button_disable: true,

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
      show_date: false,
      gender: '',
      check: false,
      contact: '',
      preferred_team: '',
      title: '',

      location_country_name:'',
      location_country: '',

      live_check_username: false,
      live_check_email: false,
      live_check_firstname: false,
      live_check_lastname: false,
      live_check_phone: false,
      live_check_dob: false,
      live_check_city: false,
      live_check_state: false,
      live_check_zipcode: false,
      live_check_passwordmatch: false,

      password_too_simple: false
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
    this.onInputChange_gender           = this.onInputChange_gender.bind(this);
    this.onInputChange_checkbox         = this.onInputChange_checkbox.bind(this);
    this.onInputChange_contact          = this.onInputChange_contact.bind(this);
    this.onInputChange_team             = this.onInputChange_team.bind(this);
    this.onInputChange_title            = this.onInputChange_title.bind(this);
    this.handle_one_click               = this.handle_one_click.bind(this);
  }

  componentDidMount() {
    this.props.authCheckState()
    .then(res => {
      if (res === AUTH_RESULT_SUCCESS) {
        this.props.history.push('/'); 
      } 
    });

    axios.get('https://ipapi.co/json/')
    .then(res => {
      this.setState({
        location_country_name: res.data.country_name, 
        location_country: res.data.country})
    })
  }

  async onInputChange_username(event){
    if (!event.target.value.match(/^[0-9a-zA-Z]+$/)){
      this.setState({live_check_username: true, button_disable: true})
    }else{
      this.setState({live_check_username: false})
    }
    await this.setState({username: event.target.value});
    this.check_button_disable()
  }

  async onInputChange_email(event){
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if (!event.target.value.match(re)){
      this.setState({live_check_email: true, button_disable: true,})
    }else{
      this.setState({live_check_email: false})
    }
    await this.setState({email: event.target.value});
    this.check_button_disable()
  }

  async onInputChange_password1(event){

    if (!event.target.value.match(/^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$/)){
      this.setState({password_too_simple: true, button_disable: true})
    }else{
      this.setState({password_too_simple: false})
    }

    if (this.state.password2 !== event.target.value){
      this.setState({live_check_passwordmatch: true, button_disable: true,})
    }else{
      this.setState({live_check_passwordmatch: false})
    }
    await this.setState({password1: event.target.value});
    this.check_button_disable()
  }

  async onInputChange_password2(event){
    if (this.state.password1 !== event.target.value){
      this.setState({live_check_passwordmatch: true, button_disable: true,})
    }else{
      this.setState({live_check_passwordmatch: false})
    }
    await this.setState({password2: event.target.value});
    this.check_button_disable()
  }

  async onInputChange_first_name(event){
    if (!event.target.value.match(/^[a-zA-Z]+$/)){
      this.setState({live_check_firstname: true, button_disable: true,})
    }else{
      this.setState({live_check_firstname: false})
    }
    await this.setState({first_name: event.target.value});
    this.check_button_disable()
  }

  async onInputChange_last_name(event){
    if (!event.target.value.match(/^[a-zA-Z]+$/)){
      this.setState({live_check_lastname: true, button_disable: true,})
    }else{
      this.setState({live_check_lastname: false})
    }
    await this.setState({last_name: event.target.value});
    this.check_button_disable()
  }

  async onInputChange_phone(phone){
    if (phone && phone.length <= 20 && phone.length >= 6){
        await this.setState({live_check_phone: false, phone: phone})
        this.check_button_disable()
    }else{
        this.setState({live_check_phone: true, button_disable: true, phone: phone})
    }
  }

  async onInputChange_date_of_birth(event){
    if (!event.target.value.match(/^([0-9]{2})\/([0-9]{2})\/([0-9]{4})$/)){
      this.setState({live_check_dob: true, button_disable: true})
    }else{
      this.setState({live_check_dob: false})
    }
    await this.setState({date_of_birth: event.target.value});
    this.check_button_disable()
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

  async onInputChange_city(event){
    if (!event.target.value.match(/^[a-zA-Z\s]+$/)){
      this.setState({live_check_city: true, button_disable: true,})
    }else{
      this.setState({live_check_city: false})
    }
    await this.setState({city: event.target.value});
    this.check_button_disable()
  }

  async onInputChange_zipcode(event){
    if (!event.target.value.match(/^[0-9]+$/)){
      this.setState({live_check_zipcode: true, button_disable: true,})
    }else{
      this.setState({live_check_zipcode: false})
    }
    await this.setState({zipcode: event.target.value});
    this.check_button_disable()
  }

  async onInputChange_state(event){
    if (!event.target.value.match(/^[a-zA-Z]+$/)){
      this.setState({live_check_state: true, button_disable: true,})
    }else{
      this.setState({live_check_state: false})
    }
    await this.setState({state: event.target.value});
    this.check_button_disable()
  }

  toggleShow() {
    this.setState({ hidden: !this.state.hidden });
  }

  onInputChange_gender(event){
    this.setState({gender: event.value})
  }

  onInputChange_checkbox(event){
    this.setState({check: !this.state.check})
  }

  onInputChange_contact(event){
    this.setState({contact: event.value})
  }

  onInputChange_team(event){
    this.setState({preferred_team: event.target.value});
  }

  onInputChange_title(event){
    this.setState({title: event.target.value});
  }

  async onInputChange_date(date){
    var res = date.toString().split(" ");
    var month = res[1]
    var day = res[2]
    var year = res[3]
    
    var today = new Date();
    var cur_year = today.getFullYear();
    var cur_month = today.getMonth()+1 ;
    var cur_day = today.getDate();

    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    var months_to = [ '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    month = months_to[months.indexOf(month)]
    if (parseInt(year) > cur_year || (parseInt(year) === cur_year && parseInt(month) > cur_month) || (parseInt(year) === cur_year && parseInt(month) === cur_month && parseInt(day) > cur_day))
    {
      var result = month + '/' + day + '/' + year
      await this.setState({date_of_birth: result})
      this.setState({live_check_dob: true, button_disable: true})
    }else{
      var result = month + '/' + day + '/' + year
      await this.setState({date_of_birth: result})
      this.setState({live_check_dob: false})
      this.check_button_disable()
    }
  }

  check_button_disable(){
    //console.log(this.state.username, this.state.email, this.state.first_name, this.state.last_name, this.state.date_of_birth, this.state.phone, this.state.city, this.state.country, this.state.state, this.state.zipcode)
    if (!this.state.live_check_username && this.state.username && 
      !this.state.live_check_email && this.state.email && 
      !this.state.live_check_firstname && this.state.first_name && 
      !this.state.live_check_lastname && this.state.last_name && 
      !this.state.live_check_dob && this.state.date_of_birth && 
      !this.state.live_check_phone && this.state.phone && 
      !this.state.live_check_city && this.state.city && 
      !this.state.live_check_state && this.state.state && 
      !this.state.live_check_zipcode && this.state.zipcode &&
      this.state.password1 && this.state.password2 &&
      !this.state.password_too_simple){

      this.setState({button_disable: false})
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
        alert(message_username + username + '  ' + message_password + password)
        
        localStorage.setItem('username', username);
        localStorage.setItem('password', password);
        localStorage.setItem('one-click', 'true');

        localStorage.removeItem('remember_username');
        localStorage.removeItem('remember_password');
        localStorage.removeItem('remember_check');

        this.props.history.push('/login/')
    })
  }

  onFormSubmit(event){
    event.preventDefault();

    this.setState({errorCode: ''})

    const referrer_id = this.props.location.pathname.slice(8)

    if (!referrer_id){
    this.props.authSignup(this.state.username, this.state.email, this.state.password1, this.state.password2, this.state.first_name, this.state.last_name, this.state.phone.slice(1), this.state.date_of_birth, this.state.street_address_1, this.state.street_address_2, this.state.country ? this.state.country : this.state.location_country_name, this.state.city, this.state.zipcode, this.state.state, this.state.gender, this.state.check, this.state.contact, this.state.preferred_team, this.state.title)
    .then((res) => {
      this.props.history.push('/activation');
      axios.post(API_URL + `users/api/activate/`, {email: this.state.email })
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
    this.props.authSignup(this.state.username, this.state.email, this.state.password1, this.state.password2, this.state.first_name, this.state.last_name, this.state.phone.slice(1), this.state.date_of_birth, this.state.street_address_1, this.state.street_address_2, this.state.country ? this.state.country : this.state.location_country_name, this.state.city, this.state.zipcode, this.state.state, this.state.gender, this.state.check, this.state.contact, this.state.preferred_team, this.state.title)
      .then((res) => {
        this.props.history.push('/activation');
        axios.post(API_URL + `users/api/activate/`, { email: this.state.email })
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

  render() {

    const showErrors = () => {
      if (this.state.username_error) {
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
      } else if (this.state.errorCode === errors.GENDER_NOT_VALID){
        return (
          <div style={{color: 'red'}}>
            <FormattedMessage id="sign.gendererror" defaultMessage='Gender not selected' /> 
          </div>
        );
      }else if (!this.state.username_error && !this.state.email_error && !this.state.password_error){
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
            *<FormattedMessage id="signup.username" defaultMessage='Username: ' />  
            </b></label>
            <input
                placeholder="Wilson"
                className="form-control"
                value={this.state.username}
                onChange={this.onInputChange_username}
            />
          </div>

          {this.state.live_check_username && <div style={{color: 'red'}}> <FormattedMessage  id="error.username" defaultMessage='Username not valid' /> </div>}

          <div>
            <label><b>
            *<FormattedMessage id="signup.email" defaultMessage='Email: ' />    
            </b></label>
            <input
                placeholder="example@gmail.com"
                className="form-control"
                value={this.state.email}
                onChange={this.onInputChange_email}
            />
          </div>

          {this.state.live_check_email && <div style={{color: 'red'}}> <FormattedMessage  id="error.email" defaultMessage='Email address not valid' /> </div>}

          <div>
            <label><b>
            *<FormattedMessage id="signup.password" defaultMessage='Password: ' />   
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
            *<FormattedMessage id="signup.confirm" defaultMessage='Confirm: ' />   
            </b></label>
            <input
                type = 'password'
                placeholder="password"
                className="form-control"
                value={this.state.password2}
                onChange={this.onInputChange_password2}
            />
          </div>

          {this.state.password_too_simple && <div style={{color: 'red'}}> <FormattedMessage  id="signup.password_simple" defaultMessage='Password is too simple' /> </div>}
          {this.state.live_check_passwordmatch && <div style={{color: 'red'}}> <FormattedMessage  id="error.passwordnotmatch" defaultMessage='Two password you entered do not match' /> </div>}

          <div>
            <label><b>
            <FormattedMessage id="sign.title" defaultMessage='Title: ' />  
            </b></label>
            <input
                placeholder="Mr./Mrs."
                className="form-control"
                value={this.state.title}
                onChange={this.onInputChange_title}
            />
          </div>

          <div>
            <label><b>
            *<FormattedMessage id="signup.firstName" defaultMessage='First Name: ' />     
            </b></label>
            <input
                placeholder="Vicky"
                className="form-control"
                value={this.state.first_name}
                onChange={this.onInputChange_first_name}
            />
          </div>

          {this.state.live_check_firstname && <div style={{color: 'red'}}> <FormattedMessage  id="error.firstname" defaultMessage='First name not valid' /> </div>}

          <div>
            <label><b>
            *<FormattedMessage id="signup.lastName" defaultMessage='Last Name: ' />   
            </b></label>
            <input
                placeholder="Stephen"
                className="form-control"
                value={this.state.last_name}
                onChange={this.onInputChange_last_name}
            />
          </div>

          {this.state.live_check_lastname && <div style={{color: 'red'}}> <FormattedMessage  id="error.lastname" defaultMessage='Last name not valid' /> </div>}

          <div>
            <label><b>
            *<FormattedMessage id="signup.phone" defaultMessage='Phone: ' />    
            </b></label>
            
            <div style={{width: '250px'}}>
              <PhoneInput
                country={this.state.location_country}
                placeholder="Enter phone number"
                value={ this.state.phone }
                onChange={ this.onInputChange_phone } 
              />
            </div>
          </div>

          {this.state.live_check_phone && <div style={{color: 'red'}}> <FormattedMessage  id="error.phone" defaultMessage='Phone number not valid' /> </div>}

          <div className='rows'>
            <label><b>
            *<FormattedMessage id="signup.dob" defaultMessage='Date of birth: ' />  
            </b></label>

            {
              <div style={{color: 'blue'}}>  {this.state.date_of_birth}  </div>
            }

          </div>

          <div>
            <div onClick={() => {this.setState({show_date: !this.state.show_date})}} style={{color: 'blue'}}>
                <FormattedMessage id="sign.show_date" defaultMessage='Show date' />
            </div>
          </div>

            {
              this.state.show_date && 
              <Calendar
                onChange={this.onInputChange_date}
              />
            }

          {this.state.live_check_dob && <div style={{color: 'red'}}> <FormattedMessage  id="error.dateofbirth" defaultMessage='Date of birth not valid' /> </div>}

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
            *<FormattedMessage id="signup.city" defaultMessage='City: ' />  
            </b></label>
            <input
                placeholder="Mountain View"
                className="form-control"
                value={this.state.city}
                onChange={this.onInputChange_city}
            />
          </div> 

          {this.state.live_check_city && <div style={{color: 'red'}}> <FormattedMessage  id="error.city" defaultMessage='City not valid' /> </div>}

          <div>
            <label><b>
            *<FormattedMessage id="signup.state" defaultMessage='State: ' />  
            </b></label>
            <input
                placeholder="CA"
                className="form-control"
                value={this.state.state}
                onChange={this.onInputChange_state}
            />
          </div>       

          {this.state.live_check_state && <div style={{color: 'red'}}> <FormattedMessage  id="error.state" defaultMessage='State not valid' /> </div>}    

          <div>
            <label><b>
            *<FormattedMessage id="signup.country" defaultMessage='Country: ' />   
            </b></label>
            <CountryDropdown
              showDefaultOption={true}
              defaultOptionLabel={this.state.location_country_name}
              value={this.state.country}
              onChange={this.onInputChange_country} 
            />
          </div>         


          <div>
            <label><b>
            *<FormattedMessage id="signup.zipcode" defaultMessage='Zipcode: ' />    
            </b></label>
            <input
                placeholder="92612"
                className="form-control"
                value={this.state.zipcode}
                onChange={this.onInputChange_zipcode}
            />
          </div> 

          {this.state.live_check_zipcode && <div style={{color: 'red'}}> <FormattedMessage  id="error.zipcode" defaultMessage='Zipcode not valid' /> </div>}

          <div>
            <label><b>
              <FormattedMessage id="sign.gender" defaultMessage='Gender: ' />    
            </b></label>
            <div style = {{width: '100px', height: '15px'}}>  
              <Dropdown 
                options={options} 
                onChange={this.onInputChange_gender} 
                value={this.state.gender} 
              />
            </div>
          </div>

          <br />

          <div>
            <label><b>
              <FormattedMessage id="sign.eighteen" defaultMessage='Over eighteen: ' />    
            </b></label>
            <input
              type="checkbox"
              checked={this.state.check}
              onChange={this.onInputChange_checkbox} 
            />
          </div>

          <br />

          <div>
            <label><b>
              <FormattedMessage id="sign.contact" defaultMessage='Preferred contact method: ' />    
            </b></label>
            <div style = {{width: '150px', height: '15px'}}>  
              <Dropdown 
                options={contact} 
                onChange={this.onInputChange_contact} 
                value={this.state.contact} 
              />
            </div>
          </div>

          <br />

          <div>
            <label><b>
              <FormattedMessage id="sign.team" defaultMessage='Preferred team: ' />    
            </b></label>
            <input
                placeholder="Thunder"
                className="form-control"
                value={this.state.preferred_team}
                onChange={this.onInputChange_team}
            />
          </div>        

          <br />  
          
          <span className="input-group-btn">
              <button disabled = {this.state.button_disable} type="submit" className="btn btn-secondary"> 
                <FormattedMessage id="signup.submit" defaultMessage='Submit' />    
              </button>
          </span>          

        </form>

        <FormattedMessage id="login.one-click" defaultMessage='Or try one click signup' />

        <button style={{marginLeft: width * 0.02}} onClick={this.handle_one_click}>
            <FormattedMessage id="login.signup" defaultMessage='Signup' />
        </button>

        <br />

        <NavLink to='/' style={{ textDecoration: 'none', color: 'red' }}>
            <button style={{color: 'red'}}>
                <FormattedMessage id="signup.cancel" defaultMessage='Cancel' />
            </button>
        </NavLink>


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

export default injectIntl(connect(mapStateToProps, {authSignup, authCheckState})(Signup));