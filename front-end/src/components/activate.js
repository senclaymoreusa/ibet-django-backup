import React, { Component } from 'react';
import { FormattedMessage } from 'react-intl';
import { NavLink } from 'react-router-dom';
import axios from 'axios';

const API_URL = process.env.REACT_APP_REST_API;

class Activate extends Component {

    constructor(props){
        super(props);

        this.state = {
           valid: true,
           loading: true,
           error: ''
        }
    }
  
  componentDidMount() {
    const { token } = this.props.match.params;
    axios.post(API_URL + `users/api/activate-verify/?token=${token}`)
    .then(res => {
        if (res.data === 'Success'){
            this.setState({loading: false, error: ''});
        }else{
            this.setState({error: res.data});
        }
      })
    }
 
  render(){
      return (
        <div> 
          {
            !this.state.loading && <FormattedMessage id="activate.success" defaultMessage='You have successfully activated your account' />
          }
          <br/> 
            <NavLink to='/' style={{ textDecoration: 'none' }}><FormattedMessage id="profile.back" defaultMessage='Back' /></NavLink>
          <br/>
          {
            <div style={{color: 'red'}}> {this.state.error} </div>
          }
       </div>
      )
   }
}

export default Activate;