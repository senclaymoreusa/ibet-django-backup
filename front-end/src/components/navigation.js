import React, { Component } from 'react';
import Select from 'react-select';
import { NavLink, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import { logout, handle_search, setLanguage } from '../actions';
import IoAndroidPerson from "react-icons/lib/io/android-person";
import '../css/nav.css';
import {push as BurgerMenu} from 'react-burger-menu'

let styles = {
  bmBurgerButton: {
      position: 'relative',
      width: '100px',
      height: '30px',
      top: '5px'
  },
  bmBurgerBars: {
      background: '#373a47'
  },
  bmCrossButton: {
      height: '24px',
      width: '24px'
  },
  bmCross: {
      background: '#bdc3c7'
  },
  bmMenu: {
      background: 'white',
      padding: '2.5em 1.5em 0',
      fontSize: '1.15em'
  },
  bmMorphShape: {
      fill: '#373a47'
  },
  bmItemList: {
      color: '#b8b7ad',
      padding: '0.8em'
  },
  bmOverlay: {
      background: 'rgba(0, 0, 0, 0.3)'
  }
};

const languages = [
  { value: 'en', label: 'English (en)' },
  { value: 'zh-hans', label: '簡體中文 (zh-hans)' },
  { value: 'fr', label: 'français (fr)' }
];

export class Navigation extends Component {

    constructor(props){
        super(props);

        this.state = { 
          term: '', 

          facebooklogin: false, 
          userID: "",
          name: "",
          email: "",
          picture: "" 
        };

        this.onInputChange = this.onInputChange.bind(this);
        this.onFormSubmit = this.onFormSubmit.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    componentWillReceiveProps(props) {
      this.setState({ term: '' });
    }

    componentDidMount() {
       var fackbooklogin = localStorage.getItem('facebook')
       this.setState({facebooklogin: fackbooklogin})
       var fackbookObj = JSON.parse(localStorage.getItem('facebookObj'))
       if (fackbooklogin === 'true'){
        this.setState({
          userID:   fackbookObj.userID, 
          name:     fackbookObj.name,
          email:    fackbookObj.email,
          picture:  fackbookObj.picture
       })
       }
    }

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
        <div className="nav" >
          
            <div className='logo' onClick={ () => {this.props.history.push('/')}}>
               ibet 
            </div>
           
            <div className='game'>
                <NavLink to='/game_type/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.games" defaultMessage='Games' /></NavLink>
            </div>

            <form onSubmit={this.onFormSubmit} className="search">

              <FormattedMessage id="nav.placeholder" defaultMessage="Search games...">

              {
                  placeholder => 
                  <input type="text" 
                    placeholder={placeholder} 
                    className="form-control" 
                    value={this.state.term} 
                    onChange={this.onInputChange} 
                  />
              }
              
              </FormattedMessage>

              <span className="input-group-btn">
                <NavLink to = {`/game_search/${this.state.term}`}  style={{ textDecoration: 'none' }} onClick={() => {window.location.reload()}}>
                    <button type="submit" className="cursor"> <FormattedMessage id="nav.search" defaultMessage='Search' /></button>
                </NavLink>
              </span>

            </form>


            <div className='language'>
              <Select
                value={option}
                onChange={this.handleChange}
                options={languages}
              />
            </div>

            {
              this.props.isAuthenticated ?
              <div>
                <BurgerMenu styles={styles} right 
                    customBurgerIcon={ 
                      <div className='row account' >
                        
                        <div>
                            <IoAndroidPerson /> 
                        </div>
                 
                        <FormattedMessage id="nav.account" defaultMessage="Account" /> 
                      </div>
                    }>
                    <div> 
                        <NavLink to = '/profile/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.profile" defaultMessage='Profile' /></NavLink>
                    </div>
                    
                    <div>
                        <NavLink to = '/referral/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.referral" defaultMessage='Refer new user' /></NavLink>
                    </div>

                    <div>
                        <NavLink to = '/' 
                          style={{ textDecoration: 'none' }}
                          onClick={()=>{
                          this.props.logout()
                          window.location.reload()
                          }}><FormattedMessage id="nav.logout" defaultMessage='Logout' />
                        </NavLink>
                    </div>

                </BurgerMenu>
              </div>
              :
              <div> </div>
            }

            
            {/*       

              Save this for later use

              this.state.facebooklogin === 'true' ?
                <div className = 'rows' style = {{width: "100px", heihgt: '50px'}}>
                  <div> 
                    <img style = {{width: '30px', height: '30px'}} src={this.state.picture} alt={this.state.name} />
                  </div>
                  <div>
                    <h2 style={{width: "100px", margin: 'auto'}}> {this.state.name} </h2>
                  </div>
                </div>
              :
                  <div> </div>
            */}

            {
              this.props.isAuthenticated || this.state.facebooklogin === 'true' ?
              
              <div>
                {/*
                <NavLink to = '/' style={{ textDecoration: 'none' }} onClick={()=>{
                  this.props.logout()
                  window.location.reload()
                  }}><FormattedMessage id="nav.logout" defaultMessage='Logout' /></NavLink>
                */}
              </div>

              :
              <div className='row'> 
                  <div className='signup cursor' onClick={ () => {this.props.history.push('/signup/')}}>
                      <FormattedMessage id="login.signup" defaultMessage='Signup' /> 
                  </div>

                  <div className='login row cursor'  onClick={ () => {this.props.history.push('/login/')}}> 
                      <IoAndroidPerson />
                      <FormattedMessage id="nav.login" defaultMessage='Login' /> 
                  </div>
              </div>
            }
          
          
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