import React, { Component } from 'react';
import Select from 'react-select';
import { NavLink, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { logout, handle_search, setLanguage } from '../actions';

const languages = [
  { value: 'en', label: 'English' },
  { value: 'zh-hans', label: 'Chinese' },
  { value: 'fr', label: 'French' }
];

class Navigation extends Component {

    constructor(props){
        super(props);

        this.state = { term: '' };
        this.onInputChange = this.onInputChange.bind(this);
        this.onFormSubmit = this.onFormSubmit.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    componentDidMount() {}

    handleChange = (languageOption) => {
      this.setState({ languageOption });
      this.props.setLanguage(languageOption.value)
      .then((res) => {
        // console.log("language change to:" + res.data);
      });
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

      let lang = this.props.lang;
      if (lang === 'zh') {
        lang = 'zh-hans';
      }
      let arr = languages.filter(value => {
        return value.value === lang;
      });
      const option = { value: lang, label: arr[0].label };

      return (
        <div className="Home" style={{marginTop: 30, marginRight: 50}}>
          <div className="category">
            <div>
                <NavLink to='/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.title" defaultMessage='Home' /></NavLink>
            </div>
            <div>
                <NavLink to='/books/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.books" defaultMessage='All books' /></NavLink>
            </div>
            <div>
                <NavLink to='/authors/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.authors" defaultMessage='All authors' /></NavLink>
            </div>
            <div>
                <NavLink to='/game_type/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.games" defaultMessage='All Games' /></NavLink>
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
                      <NavLink to='/game_search' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.search" defaultMessage='Search' /></NavLink>
                    </button>
                </span>
            </form>
            {
              this.props.isAuthenticated ?
              <NavLink to = '/profile/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.profile" defaultMessage='Profile' /></NavLink>
              :
              <div> </div>
            }

            {
              this.props.isAuthenticated ?
              
              <div>
                <NavLink to = '/' style={{ textDecoration: 'none' }} onClick={()=>{this.props.logout()}}><FormattedMessage id="nav.logout" defaultMessage='Logout' /></NavLink>
              </div>
              :
              <div> 
                  <NavLink to='/login/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.login" defaultMessage='Login' /></NavLink> 
              </div>
            }
          </div>
          <Select
          value={option}
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
        error: state.auth.error,
        lang: state.language.lang,
    }
}
  
export default withRouter(connect(mapStateToProps, {logout, handle_search, setLanguage})(Navigation));