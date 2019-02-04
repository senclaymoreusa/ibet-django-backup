import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import { connect } from 'react-redux';
import { logout, handle_search } from '../actions'

class Navigation extends Component {

    constructor(props){
        super(props);
        this.state = { term: '' };
        this.onInputChange = this.onInputChange.bind(this);
        this.onFormSubmit = this.onFormSubmit.bind(this);
    }

    onInputChange(event){
        this.setState({term: event.target.value});
        this.props.handle_search(event.target.value)
    }
    onFormSubmit(event){
        event.preventDefault();
        this.setState({ term: '' });
    }

    render() {
      return (
        <div className="Home" style={{marginTop: 30, marginRight: 50}}>
          <div className="category">
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

            <form onSubmit={this.onFormSubmit} className="input-group">
                <input
                    placeholder="Search games..."
                    className="form-control"
                    value={this.state.term}
                    onChange={this.onInputChange}
                />
                <span className="input-group-btn">
                    <button type="submit" className="btn btn-secondary"> 
                      <NavLink to='/game_search'> Search </NavLink>
                    </button>
                </span>
            </form>

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
  
export default connect(mapStateToProps, {logout, handle_search})(Navigation);