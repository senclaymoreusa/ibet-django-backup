import React, { Component } from 'react';
import Select from 'react-select';
import { NavLink, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { logout, handle_search } from '../actions';

const languages = [
  { value: 'en', label: 'English' },
  { value: 'zh', label: 'Chinese' },
  { value: 'fr', label: 'French' }
];

class Navigation extends Component {

    constructor(props){
        super(props);
        this.state = { term: '' , languageOption: { value: 'zh', label: 'Chinese' }};
        this.onInputChange = this.onInputChange.bind(this);
        this.onFormSubmit = this.onFormSubmit.bind(this);
        // this.getInitialState = this.getInitialState.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    componentDidMount() {}

    // getInitialState() {
    //   return {languageOption: 'zh' };
    // }

    handleChange = (languageOption) => {
      this.setState({ languageOption });
      console.log(`option: `, languageOption);
      console.log(`current state`, this.state);
    }

    onInputChange(event){
        this.setState({term: event.target.value});
        this.props.handle_search(event.target.value);
    }
    onFormSubmit(event){
        this.props.history.push("/game_search");
        event.preventDefault();
        this.setState({ term: '' });
    }

    render() {
      return (
        <div className="Home" style={{marginTop: 30, marginRight: 50}}>
          <div className="category">
            <div>
                <NavLink to='/' style={{ textDecoration: 'none' }}> Home </NavLink>
            </div>
            <div>
                <NavLink to='/books/' style={{ textDecoration: 'none' }}> All books </NavLink>
            </div>
            <div>
                <NavLink to='/authors/' style={{ textDecoration: 'none' }}> All authors </NavLink>
            </div>
            <div>
                <NavLink to='/game_type/' style={{ textDecoration: 'none' }}> All Games </NavLink>
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
                      <NavLink to='/game_search' style={{ textDecoration: 'none' }}> Search </NavLink>
                    </button>
                </span>
            </form>
            {
              this.props.isAuthenticated ?
              <NavLink to = '/profile/' style={{ textDecoration: 'none' }}> Profile </NavLink>
              :
              <div> </div>
            }

            {
              this.props.isAuthenticated ?
              
              <div>
                <NavLink to = '/' style={{ textDecoration: 'none' }} onClick={()=>{this.props.logout()}}> Logout </NavLink>
              </div>
              :
              <div> 
                  <NavLink to='/login/' style={{ textDecoration: 'none' }}> Login </NavLink> 
              </div>
            }
          </div>
          {/* <select 
            value={this.state.languageCode} 
            onChange={this.handleChange} 
          >
            <option value="en">English</option>
            <option value="zh">Chinese</option>
            <option value="fr">French</option>
          </select> */}
          <Select
            value={this.state.languageOption}
            onChange={this.handleChange}
            options={languages}
          />
        </div>
      );
    }
  }

const mapStateToProps = (state) => {
    const { token } = state.auth;
    return {
        isAuthenticated: token !== null && token !== undefined, 
        error:state.auth.error
    }
}
  
export default withRouter(connect(mapStateToProps, {logout, handle_search})(Navigation));