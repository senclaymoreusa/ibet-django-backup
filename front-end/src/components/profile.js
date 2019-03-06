import React, { Component } from 'react';
import { authCheckState, AUTH_RESULT_FAIL } from '../actions';
import { connect } from 'react-redux';
import axios from 'axios';
import { NavLink} from 'react-router-dom';
import { FormattedMessage } from 'react-intl';
import { config } from '../util_config';

const API_URL = process.env.REACT_APP_REST_API;

class Profile extends Component {

    state = {
        data: {}
    }

    componentDidMount() {
      this.props.authCheckState()
      .then(res => {
        if (res === AUTH_RESULT_FAIL) {
          this.props.history.push('/'); 
        } else {
          const token = localStorage.getItem('token');
          config.headers["Authorization"] = `Token ${token}`;

          return axios.get(API_URL + 'users/api/user/', config)
          .then(res => {
              this.setState({data: res.data});
          }) 
        }
      });
    }


    render(){
      return (
        <div>
        {
          <div>
            <div> <b>
            <FormattedMessage id="profile.username" defaultMessage='Username: ' />
              </b>  {this.state.data.username} </div>
            <div> <b>
            <FormattedMessage id="profile.email" defaultMessage='Email: ' />
              </b> {this.state.data.email} </div>
            <div> <b>
            <FormattedMessage id="profile.firstName" defaultMessage='First Name: ' />
              </b>  {this.state.data.first_name}  </div>
            <div> <b>
            <FormattedMessage id="profile.lastName" defaultMessage='Last Name: ' />
            </b>  {this.state.data.last_name}  </div>
            <div> <b>
            <FormattedMessage id="profile.phone" defaultMessage='Phone: ' />
            </b>  {this.state.data.phone}  </div>
            <div> <b>
            <FormattedMessage id="profile.dob" defaultMessage='Date of Birth: ' />
            </b>  {this.state.data.date_of_birth}  </div>
            <div> <b>
            <FormattedMessage id="profile.street1" defaultMessage='Street Address 1: ' />
            </b>  {this.state.data.street_address_1}  </div>
            <div> <b>
            <FormattedMessage id="profile.street2" defaultMessage='Street Address 2: ' />
            </b>  {this.state.data.street_address_2}  </div>
            <div> <b>
            <FormattedMessage id="profile.country" defaultMessage='Country: ' />
            </b>  {this.state.data.country}  </div>
            <div> <b>
            <FormattedMessage id="profile.city" defaultMessage='City: ' />
            </b>  {this.state.data.city}  </div>
            <div> <b>
            <FormattedMessage id="profile.zipcode" defaultMessage='Zipcode: ' />
            </b>  {this.state.data.zipcode}  </div>
            <div> <b>
            <FormattedMessage id="profile.state" defaultMessage='State: ' />
            </b>  {this.state.data.state}  </div>
            <button className="btn btn-secondary"> 
                <NavLink to='/update_profile' style={{ textDecoration: 'none' }}><FormattedMessage id="profile.update" defaultMessage='Update' /></NavLink> 
            </button>
            <button className="btn btn-secondary"> 
                <NavLink to='/' style={{ textDecoration: 'none' }}><FormattedMessage id="profile.back" defaultMessage='Back' /></NavLink> 
            </button>
          </div>
        } 
        </div>
      )
    }
}

export default connect(null, {authCheckState})(Profile);