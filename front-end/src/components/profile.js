import React, { Component } from 'react';
import { authCheckState, AUTH_RESULT_FAIL } from '../actions';
import { connect } from 'react-redux';
import axios from 'axios';
import { NavLink} from 'react-router-dom';

const API_URL = process.env.REACT_APP_REST_API

class Profile extends Component {

    state = {
        data: {}
    }

    componentDidMount() {
      this.props.authCheckState()
      .then(res => {
        if (res == AUTH_RESULT_FAIL) {
          this.props.history.push('/'); 
        } else {
          const token = localStorage.getItem('token');
          const config = {
            headers: {
              "Content-Type": "application/json"
            }
          };
          config.headers["Authorization"] = `Token ${token}`;

          return axios.get(API_URL + 'users/api/user/', config)
          .then(res => {
              this.setState({data: res.data});
          }) 
        }
      });
    }

    redirect() {
      return (
        this.props.history.push('/')
      )
    }

    render(){
      return (
        <div>
        {
          <div>
            <div> <b>Username:</b>  {this.state.data.username} </div>
            <div> <b>Email:</b> {this.state.data.email} </div>
            <div> <b>First Name: </b>  {this.state.data.first_name}  </div>
            <div> <b>Last Name: </b>  {this.state.data.last_name}  </div>
            <div> <b>Phone: </b>  {this.state.data.phone}  </div>
            <div> <b>Date of Birth: </b>  {this.state.data.date_of_birth}  </div>
            <div> <b>Street Address 1: </b>  {this.state.data.street_address_1}  </div>
            <div> <b>Street Address 2: </b>  {this.state.data.street_address_2}  </div>
            <div> <b>Country: </b>  {this.state.data.country}  </div>
            <div> <b>City: </b>  {this.state.data.city}  </div>
            <div> <b>Zipcode: </b>  {this.state.data.zipcode}  </div>
            <div> <b>State: </b>  {this.state.data.state}  </div>
            <button className="btn btn-secondary"> 
                <NavLink to='/update_profile' style={{ textDecoration: 'none' }}> Update </NavLink> 
            </button>
            <button className="btn btn-secondary"> 
                <NavLink to='/' style={{ textDecoration: 'none' }}> Back </NavLink> 
            </button>
          </div>
        } 
        </div>
      )
    }
}

export default connect(null, {authCheckState})(Profile);