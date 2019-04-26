import React, { Component } from 'react';
import axios from 'axios';
import { NavLink, withRouter } from 'react-router-dom';
import { config } from '../util_config';
import { FormattedMessage } from 'react-intl';
import { errors } from './errors';
import { CountryDropdown } from 'react-country-region-selector';
import Calendar from 'react-calendar';


const API_URL = process.env.REACT_APP_REST_API;

class Update extends Component {

    constructor(props){
        super(props);

        this.state = {
            username: '',
            email: '',
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
            
            fetched_data: {},
            errorCode: '',

            button_disable: false,
            show_date: false,

            live_check_firstname: false,
            live_check_lastname: false,
            live_check_dob: false,
            live_check_country: false,
            live_check_city: false,
            live_check_state: false,
            live_check_zipcode: false,
        }

        this.onInputChange_first_name       = this.onInputChange_first_name.bind(this);
        this.onInputChange_last_name        = this.onInputChange_last_name.bind(this);
        this.onInputChange_date_of_birth    = this.onInputChange_date_of_birth.bind(this);
        this.onInputChange_street_address_1 = this.onInputChange_street_address_1.bind(this);
        this.onInputChange_street_address_2 = this.onInputChange_street_address_2.bind(this);
        this.onInputChange_country          = this.onInputChange_country.bind(this);
        this.onInputChange_city             = this.onInputChange_city.bind(this);
        this.onInputChange_zipcode          = this.onInputChange_zipcode.bind(this);
        this.onInputChange_state            = this.onInputChange_state.bind(this);
        this.onFormSubmit                   = this.onFormSubmit.bind(this);
    }
    
    async componentDidMount() {
      const token = localStorage.getItem('token');
      config.headers["Authorization"] = `Token ${token}`;

      await axios.get(API_URL + 'users/api/user/', config)
        .then(res => {
            this.setState({fetched_data: res.data})
        })

      this.setState({
          username:         this.state.fetched_data.username,
          email:            this.state.fetched_data.email,
          first_name:       this.state.fetched_data.first_name,
          last_name:        this.state.fetched_data.last_name,
          phone:            this.state.fetched_data.phone,
          date_of_birth:    this.state.fetched_data.date_of_birth,
          street_address_1: this.state.fetched_data.street_address_1,
          street_address_2: this.state.fetched_data.street_address_2,
          country:          this.state.fetched_data.country,
          city:             this.state.fetched_data.city,
          zipcode:          this.state.fetched_data.zipcode,
          state:            this.state.fetched_data.state
    })
    }

    onInputChange_first_name(event){
        if (!event.target.value.match(/^[a-zA-Z]+$/)){
            this.setState({live_check_firstname: true, button_disable: true})
        }else{
            this.setState({live_check_firstname: false})
            this.check_button_disable()
        }
        this.setState({first_name: event.target.value});
    }

    onInputChange_last_name(event){
        if (!event.target.value.match(/^[a-zA-Z]+$/)){
            this.setState({live_check_lastname: true, button_disable: true})
          }else{
            this.setState({live_check_lastname: false})
            this.check_button_disable()
          }
        this.setState({last_name: event.target.value});
    }

    async onInputChange_date_of_birth(date){
        var res = date.toString().split(" ");
        var month = res[1];
        var day = res[2];
        var year = res[3];
        
        var today = new Date();
        var cur_year = today.getFullYear();
        var cur_month = today.getMonth()+1 ;
        var cur_day = today.getDate();
    
        var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        var months_to = [ '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        month = months_to[months.indexOf(month)]
        if (parseInt(year) > cur_year || (parseInt(year) === cur_year && parseInt(month) > cur_month) || (parseInt(year) === cur_year && parseInt(month) === cur_month && parseInt(day) > cur_day))
        {
          var result = month + '/' + day + '/' + year;
          await this.setState({date_of_birth: result});
          this.setState({live_check_dob: true, button_disable: true});
        }else{
          var result = month + '/' + day + '/' + year;
          await this.setState({date_of_birth: result});
          this.setState({live_check_dob: false});
          this.check_button_disable();
        }
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
        if (!event.target.value.match(/^[a-zA-Z\s]+$/)){
            this.setState({live_check_city: true, button_disable: true});
        }else{
            this.setState({live_check_city: false})
            this.check_button_disable()
        }
        this.setState({city: event.target.value});
    }

    onInputChange_zipcode(event){
        if (!event.target.value.match(/^[0-9]+$/)){
            this.setState({live_check_zipcode: true, button_disable: true});
        }else{
            this.setState({live_check_zipcode: false})
            this.check_button_disable()
        }
        this.setState({zipcode: event.target.value});
    }

    onInputChange_state(event){
        if (!event.target.value.match(/^[a-zA-Z]+$/)){
            this.setState({live_check_state: true, button_disable: true});
        }else{
            this.setState({live_check_state: false})
            this.check_button_disable()
        }
        this.setState({state: event.target.value});
    }

    check_button_disable(){
        if (
            !this.state.live_check_firstname && this.state.first_name && 
            !this.state.live_check_lastname && this.state.last_name && 
            !this.state.live_check_dob && this.state.date_of_birth && 
            !this.state.live_check_city && this.state.city && 
            !this.state.live_check_state && this.state.state && 
            !this.state.live_check_zipcode && this.state.zipcode){
          this.setState({button_disable: false})
        }
      }

    onFormSubmit(event){
        event.preventDefault();

        const token = localStorage.getItem('token');
        config.headers["Authorization"] = `Token ${token}`;

        const body = JSON.stringify({ 
            username:         this.state.username         ? this.state.username         : this.state.fetched_data.username, 
            email:            this.state.email            ? this.state.email            : this.state.fetched_data.email, 
            first_name:       this.state.first_name       ? this.state.first_name       : this.state.fetched_data.first_name, 
            last_name:        this.state.last_name        ? this.state.last_name        : this.state.fetched_data.last_name,
            phone:            this.state.phone            ? this.state.phone            : this.state.fetched_data.phone, 
            date_of_birth:    this.state.date_of_birth    ? this.state.date_of_birth    : this.state.fetched_data.date_of_birth,
            street_address_1: this.state.street_address_1,
            street_address_2: this.state.street_address_2,
            country:          this.state.country          ? this.state.country          : this.state.fetched_data.country,
            city:             this.state.city             ? this.state.city             : this.state.fetched_data.city,
            state:            this.state.state            ? this.state.state            : this.state.fetched_data.state,
            zipcode:          this.state.zipcode          ? this.state.zipcode          : this.state.fetched_data.zipcode
        });

        axios.put(API_URL + 'users/api/user/', body, config)
            .then(() => {
                this.props.history.push("/profile");
            })
            .catch((err) => {
                console.log(err.response);
        })
    }

    render() {
        const showErrors = () => {
            if (this.state.errorCode === errors.EMAIL_EMPTY_ERROR) {
                return (
                    <div style={{color: 'red'}}> 
                        <FormattedMessage id="sign.email_empty_error" defaultMessage='Email cannot be empty' /> 
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
              
            } else if (this.state.password_error) {
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
                        <div><b>
                        <FormattedMessage id="update_profile.username" defaultMessage='Username: ' />
                        </b> {this.state.username} </div>
                    </div>

                    <div>
                        <b>
                        <FormattedMessage id="update_profile.email" defaultMessage='Email: ' />    
                        </b> {this.state.email}
                        <button> 
                            <NavLink to='/change_email/' style={{ textDecoration: 'none' }}>
                            <FormattedMessage id="update_profile.update_email" defaultMessage='Update Email' />    
                            </NavLink>
                        </button>
                    </div>

                    <div>
                        <label><b>
                        <FormattedMessage id="update_profile.phone" defaultMessage='Phone: ' />      
                        </b> {this.state.phone} </label>
                    </div>

                    <div>
                        <label><b>
                        <FormattedMessage id="update_profile.firstName" defaultMessage='First Name: ' />       
                        </b></label>
                        <input
                            placeholder="Mike"
                            className="form-control"
                            value={this.state.first_name}
                            onChange={this.onInputChange_first_name}
                        />
                    </div>

                    {this.state.live_check_firstname && <div style={{color: 'red'}}> <FormattedMessage  id="error.firstname" defaultMessage='First name not valid' /> </div>}

                    <div>
                        <label><b>
                        <FormattedMessage id="update_profile.lastName" defaultMessage='Last Name: ' />     
                        </b></label>
                        <input
                            placeholder="Shaw"
                            className="form-control"
                            value={this.state.last_name}
                            onChange={this.onInputChange_last_name}
                        />
                    </div>

                    {this.state.live_check_lastname && <div style={{color: 'red'}}> <FormattedMessage  id="error.lastname" defaultMessage='Last name not valid' /> </div>}

                    <div>
                        <label><b>
                        <FormattedMessage id="update_profile.dob" defaultMessage='Date of Birth: ' />      
                        </b></label>
                        {this.state.date_of_birth}
                        <div onClick={() => {this.setState({show_date: !this.state.show_date})}} style={{color: 'blue'}}>
                            <FormattedMessage id="sign.show_date" defaultMessage='Show date' />
                        </div>
                    </div>

                    {
                        this.state.show_date && <Calendar
                            onChange={this.onInputChange_date_of_birth}
                            value={this.state.date}
                        />
                    }

                    {this.state.live_check_dob && <div style={{color: 'red'}}> <FormattedMessage  id="error.dateofbirth" defaultMessage='Date of birth not valid' /> </div>}

                    <div>
                        <label><b>
                        <FormattedMessage id="update_profile.street1" defaultMessage='Street Address 1: ' />    
                        </b></label>
                        <input
                            placeholder="111 World Drive"
                            className="form-control"
                            value={this.state.street_address_1}
                            onChange={this.onInputChange_street_address_1}
                        />
                    </div>

                    <div>
                        <label><b>
                        <FormattedMessage id="update_profile.street2" defaultMessage='Street Address 2: ' />    
                        </b></label>
                        <input
                            placeholder="Suite No.123"
                            className="form-control"
                            value={this.state.street_address_2}
                            onChange={this.onInputChange_street_address_2}
                        />
                    </div>

                    <div>
                        <label><b>
                        <FormattedMessage id="update_profile.country" defaultMessage='Country: ' />       
                        </b></label>
                        <CountryDropdown
                            value={this.state.country}
                            onChange={this.onInputChange_country} 
                        />
                    </div>

                    <div>
                        <label><b>
                        <FormattedMessage id="update_profile.city" defaultMessage='City: ' />    
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
                        <FormattedMessage id="update_profile.zipcode" defaultMessage='Zipcode: ' />      
                        </b></label>
                        <input
                            placeholder="96173"
                            className="form-control"
                            value={this.state.zipcode}
                            onChange={this.onInputChange_zipcode}
                        />
                    </div>

                    {this.state.live_check_zipcode && <div style={{color: 'red'}}> <FormattedMessage  id="error.zipcode" defaultMessage='Zipcode not valid' /> </div>}

                    <div>
                        <label><b>
                        <FormattedMessage id="update_profile.state" defaultMessage='State: ' />    
                        </b></label>
                        <input
                            placeholder="CA"
                            className="form-control"
                            value={this.state.state}
                            onChange={this.onInputChange_state}
                        />
                    </div>

                    {this.state.live_check_state && <div style={{color: 'red'}}> <FormattedMessage  id="error.state" defaultMessage='State not valid' /> </div>}    
                    
                    <span className="input-group-btn">
                        <button disabled = {this.state.button_disable} type="submit" className="btn btn-secondary"> 
                            <FormattedMessage id="update_profile.submit" defaultMessage='Submit' />
                        </button>
                    </span>
                </form>
                <button style={{color: 'red'}} onClick={()=>{this.props.history.push("/profile")}}> 
                    <FormattedMessage id="update_profile.cancel" defaultMessage='Cancel' /> 
                </button>

                {
                    showErrors()
                }
            </div>
        )
    }
}

export default withRouter(Update);