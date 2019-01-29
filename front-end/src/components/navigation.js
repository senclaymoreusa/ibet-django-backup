import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import { connect } from 'react-redux';
import { logout } from '../actions'

class Navigation extends Component {
    render() {
      return (
        <div className="Home" style={{marginTop: 30, marginRight: 50}}>
          <div className="category" style={{ flexDirection: 'row'}}>
            <div>
                <NavLink to='/'> Home </NavLink>
            </div>
            <div>
                <NavLink to='/books/'> All books </NavLink>
            </div>
            <div>
                <NavLink to='/authors/'> All authors </NavLink>
            </div>
            <div>
                <NavLink to='/game_type/'> All Games </NavLink>
            </div>
            {
              this.props.isAuthenticated ?
              
              <div>
                <NavLink to = '/' onClick={()=>{this.props.logout()}}> Logout </NavLink>
              </div>
              :
              <div> 
                  <NavLink to='/login/'> Login </NavLink> 
              </div>
            }
          </div>
        </div>
      );
    }
  }

const mapStateToProps = (state) => {
    return {
        isAuthenticated: state.auth.token !== null
    }
}
  
export default connect(mapStateToProps, {logout})(Navigation);