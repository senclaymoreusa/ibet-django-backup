import React, { Component } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_REST_API

class Profile extends Component {

    state = {
        data: {}
    }

    componentDidMount() {
      const token = localStorage.getItem('token');
      const config = {
        headers: {
          "Content-Type": "application/json"
        }
      };
      config.headers["Authorization"] = `Token ${token}`;

      axios.get(API_URL + 'users/api/user/', config)
        .then(res => {
            this.setState({data: res.data})
        })
    }

    render(){
      return (
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
        </div>
      )
    }
}

export default Profile;