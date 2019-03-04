import React from 'react';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { authSignup, authCheckState, AUTH_RESULT_SUCCESS } from '../actions'
import axios from 'axios';
import { messages } from './messages';

const API_URL = process.env.REACT_APP_REST_API


class Signup extends React.Component {

  constructor(props){
    super(props);

    this.state = {
      email_error: '',
      username_error: '',
      error: '',
  
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

  onInputChange_country(event){
    this.setState({country: event.target.value});
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

  onFormSubmit(event){
    event.preventDefault();

    if (!this.state.username){
      this.setState({error: messages.USERNAME_EMPTY_ERROR})
    }else if(!this.state.email){
      this.setState({error: messages.EMAIL_EMPTY_ERROR})
    }else if (!this.state.password1 || !this.state.password2){
      this.setState({error: messages.PASSWORD_EMPTY_ERROR})
    }else if(!this.state.first_name){
      this.setState({error: messages.FIRST_NAME_EMPTY_ERROR})
    }else if(!this.state.last_name){
      this.setState({error: messages.LAST_NAME_EMPTY_ERROR})
    }else if(!this.state.phone){
      this.setState({error: messages.PHONE_EMPTY_ERROR})
    }else if(!this.state.date_of_birth){
      this.setState({error: messages.DATEOFBIRTH_EMPTY_ERROR})
    }else if(!this.state.street_address_1 || !this.state.street_address_2){
      this.setState({error: messages.STREET_EMPTY_ERROR})
    }else if(!this.state.city){
      this.setState({error: messages.CITY_EMPTY_ERROR})
    }else if(!this.state.state){
      this.setState({error: messages.STATE_EMPTY_ERROR})
    }else if(!this.state.country){
      this.setState({error: messages.COUNTRY_EMPTY_ERROR})
    }else if(!this.state.zipcode){
      this.setState({error: messages.ZIPCODE_EMPTY_ERROR})
    }else{
      this.props.authSignup(this.state.username, this.state.email, this.state.password1, this.state.password2, this.state.first_name, this.state.last_name, this.state.phone, this.state.date_of_birth, this.state.street_address_1, this.state.street_address_2, this.state.country, this.state.city, this.state.zipcode, this.state.state)
      .then(() => {
        this.props.history.push('/');
        axios.get(API_URL + `users/api/sendemail/?case=signup&to_email_address=${this.state.email}&username=${this.state.username}&email=${this.state.email}`)
      }).catch(err => {

        if ('username' in err.response.data){
          this.setState({username_error: err.response.data.username[0]})
        }else{
          this.setState({username_error: ''})
        }

        if('email' in err.response.data){
          this.setState({email_error: err.response.data.email[0]})
        }else{
          this.setState({email_error: ''})
        }

        if ('non_field_errors' in err.response.data){
          this.setState({error: err.response.data.non_field_errors.slice(0)})
        }
      })
    }
  }

  render() {
    
    return (

      <div> 
        <form onSubmit={this.onFormSubmit} >

          <div>
            <label><b>Username:</b></label>
            <input
                placeholder="Wilson"
                className="form-control"
                value={this.state.username}
                onChange={this.onInputChange_username}
            />
          </div>

          <div>
            <label><b>Email:</b></label>
            <input
                placeholder="example@gmail.com"
                className="form-control"
                value={this.state.email}
                onChange={this.onInputChange_email}
            />
          </div>

          <div>
            <label><b>Password:</b></label>
            <input
                type = 'password'
                placeholder="password"
                className="form-control"
                value={this.state.password1}
                onChange={this.onInputChange_password1}
            />
          </div>

          <div>
            <label><b>Confirm:</b></label>
            <input
                type = 'password'
                placeholder="password"
                className="form-control"
                value={this.state.password2}
                onChange={this.onInputChange_password2}
            />
          </div>

          <div>
            <label><b>First Name:</b></label>
            <input
                placeholder="Vicky"
                className="form-control"
                value={this.state.first_name}
                onChange={this.onInputChange_first_name}
            />
          </div>

          <div>
            <label><b>Last Name:</b></label>
            <input
                placeholder="Stephen"
                className="form-control"
                value={this.state.last_name}
                onChange={this.onInputChange_last_name}
            />
          </div>

          <div>
            <label><b>Phone:</b></label>
            <input
                placeholder="9496541234"
                className="form-control"
                value={this.state.phone}
                onChange={this.onInputChange_phone}
            />
          </div>

          <div>
            <label><b>Date of birth:</b></label>
            <input
                placeholder="mm/dd/yyyy"
                className="form-control"
                value={this.state.date_of_birth}
                onChange={this.onInputChange_date_of_birth}
            />
          </div>

          <div>
            <label><b>Street Address 1:</b></label>
            <input
                placeholder="123 World Dr"
                className="form-control"
                value={this.state.street_address_1}
                onChange={this.onInputChange_street_address_1}
            />
          </div>     

          <div>
            <label><b>Street Address 2:</b></label>
            <input
                placeholder="Suite 23"
                className="form-control"
                value={this.state.street_address_2}
                onChange={this.onInputChange_street_address_2}
            />
          </div>                

          <div>
            <label><b>City:</b></label>
            <input
                placeholder="Mountain View"
                className="form-control"
                value={this.state.city}
                onChange={this.onInputChange_city}
            />
          </div> 

          <div>
            <label><b>State:</b></label>
            <input
                placeholder="CA"
                className="form-control"
                value={this.state.state}
                onChange={this.onInputChange_state}
            />
          </div>           

          <div>
            <label><b>Country:</b></label>
            <input
                placeholder="United States"
                className="form-control"
                value={this.state.country}
                onChange={this.onInputChange_country}
            />
          </div>           

          <div>
            <label><b>Zipcode:</b></label>
            <input
                placeholder="92612"
                className="form-control"
                value={this.state.zipcode}
                onChange={this.onInputChange_zipcode}
            />
          </div> 

          <span className="input-group-btn">
              <button type="submit" className="btn btn-secondary"> 
                  Submit 
              </button>
          </span>          

        </form>

        <button> 
          <NavLink to='/' style={{ textDecoration: 'none', color: 'red' }}>
            Cancel
          </NavLink>
        </button>

        {
          <div style={{color: 'red'}}> {this.state.username_error} </div>
        }
            
        {
          <div style={{color: 'red'}}> {this.state.email_error} </div>
        }

        {
          !this.state.username_error && !this.state.email_error ?
          <div style={{color: 'red'}}> {this.state.error} </div>
          :
          <div> </div>
        }

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