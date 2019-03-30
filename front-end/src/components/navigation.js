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

    componentWillReceiveProps(props) {
      this.setState({ term: '' });
    }

    componentDidMount() {}

    handleChange = (languageOption) => {
      this.setState({ languageOption });
      this.props.setLanguage(languageOption.value)
      .then((res) => {
        // console.log("language change to:" + res.data);
      });
    }

    onInputChange(event) {
      this.setState({ term: event.target.value });
    }

    // not used right now!
    onFormSubmit(event) {
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
                <NavLink to='/game_type/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.games" defaultMessage='All Games' /></NavLink>
            </div>

            <form onSubmit={this.onFormSubmit} className="input-group">
              <FormattedMessage id="nav.placeholder" defaultMessage="Search games...">
              {placeholder => <input type="text" placeholder={placeholder} className="form-control" value={this.state.term} onChange={this.onInputChange} />}
              </FormattedMessage>
              <span className="input-group-btn">
                <NavLink to = {`/game_search/${this.state.term}`}  style={{ textDecoration: 'none' }}>
                <button type="submit" className="btn btn-secondary"> <FormattedMessage id="nav.search" defaultMessage='Search' /></button>
                </NavLink>
              </span>
            </form>
            {
              this.props.isAuthenticated ?
              <div>
                  <div> 
                      <NavLink to = '/profile/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.profile" defaultMessage='Profile' /></NavLink>
                  </div>
                  
                  <div>
                      <NavLink to = '/referral/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.referral" defaultMessage='Refer new user' /></NavLink>
                  </div>
              </div>
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