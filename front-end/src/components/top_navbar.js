import React, { Component } from "react";
import { withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { logout, handle_search, setLanguage } from '../actions';
import { FormattedMessage } from 'react-intl';
import { NavLink } from 'react-router-dom';
import { push as BurgerMenu } from 'react-burger-menu'
import IoAndroidPerson from "react-icons/lib/io/android-person";

import {
    MDBNavbar, MDBNavbarBrand, MDBNavbarNav, MDBNavItem, MDBNavLink, MDBNavbarToggler, MDBCollapse, MDBFormInline,
    MDBDropdown, MDBDropdownToggle, MDBDropdownMenu, MDBDropdownItem, MDBIcon, MDBBtn
} from "mdbreact";

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

export class TopNavbar extends Component {
    constructor(props) {
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
        this.handleChange = this.handleChange.bind(this);
    }

    componentWillReceiveProps(props) {
        this.setState({ term: '' });
    }

    componentDidMount() {
        var fackbooklogin = localStorage.getItem('facebook')
        this.setState({ facebooklogin: fackbooklogin })
        var fackbookObj = JSON.parse(localStorage.getItem('facebookObj'))
        if (fackbooklogin === 'true') {
            this.setState({
                userID: fackbookObj.userID,
                name: fackbookObj.name,
                email: fackbookObj.email,
                picture: fackbookObj.picture
            })
        }
    }
    onInputChange(event) {
        this.setState({ term: event.target.value });
    }

    handleChange = (languageOption) => {
        this.setState({ languageOption });
        this.props.setLanguage(languageOption.value)
            .then((res) => {
                // console.log("language change to:" + res.data);
            });
    }

    searchInputChanged(event) {
        this.setState({ term: event.target.value });
    }

    toggleCollapse = () => {
        this.setState({ isOpen: !this.state.isOpen });
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
            <MDBNavbar color="indigo" dark expand="md">
                <MDBNavbarBrand>
                    <MDBNavLink to="./">
                        <strong className="white-text">ibet</strong>
                    </MDBNavLink>
                </MDBNavbarBrand>
                <MDBNavbarToggler onClick={this.toggleCollapse} />
                <MDBCollapse id="navbarCollapse3" isOpen={this.state.isOpen} navbar>
                    <MDBNavbarNav left>
                        <MDBNavItem active>
                            <MDBNavLink to="#!">Sports</MDBNavLink>
                        </MDBNavItem>
                        <MDBNavItem>
                            <MDBNavLink to="#!">Live Casino</MDBNavLink>
                        </MDBNavItem>
                        <MDBNavItem>
                            <MDBNavLink to="/game_type/">Games</MDBNavLink>
                        </MDBNavItem>
                        <MDBNavItem>
                            <MDBNavLink to="#!">Lottery</MDBNavLink>
                        </MDBNavItem>
                    </MDBNavbarNav>
                    <MDBNavbarNav right>

                        <MDBNavItem>
                            <MDBNavbarNav right>
                                <MDBFormInline className="md-form mr-auto m-0">
                                    <input className="form-control mr-sm-2" type="text" placeholder="Search" aria-label="Search" value={this.state.term}
                                        onChange={this.onInputChange} />
                                    <NavLink to={`/game_search/${this.state.term}`} style={{ textDecoration: 'none' }}>
                                        <MDBBtn outline color="white" size="sm" type="submit" className="mr-auto">Search</MDBBtn>
                                    </NavLink>
                                </MDBFormInline>
                            </MDBNavbarNav>
                        </MDBNavItem>
                        <MDBNavItem>
                            <MDBDropdown>
                                <MDBDropdownToggle nav caret>
                                    <span className="mr-2">Languages</span>
                                </MDBDropdownToggle>
                                <MDBDropdownMenu>
                                    <MDBDropdownItem href="#!">English (en)</MDBDropdownItem>
                                    <MDBDropdownItem href="#!">簡體中文 (zh-hans)</MDBDropdownItem>
                                    <MDBDropdownItem href="#!">Français (fr)</MDBDropdownItem>
                                </MDBDropdownMenu>
                            </MDBDropdown>
                        </MDBNavItem>
                        {
                            this.props.isAuthenticated || this.state.facebooklogin === 'true' ?
                                <div>
                                    {}
                                </div>
                                :
                                <div className='row'>
                                    <MDBNavItem>
                                        <MDBNavLink className="waves-effect waves-light" to="/signup/">
                                            Sign up <MDBIcon icon="user-plus" />
                                        </MDBNavLink>
                                    </MDBNavItem>
                                    <MDBNavItem>
                                        <MDBNavLink className="waves-effect waves-light" to="/login/">
                                            Log in <MDBIcon icon="sign-in-alt" />
                                        </MDBNavLink>
                                    </MDBNavItem>
                                </div>
                        }
                        <MDBNavItem>
                            <MDBNavLink className="waves-effect waves-light" to="/signup/">
                                Sign up <MDBIcon icon="user-plus" />
                            </MDBNavLink>
                        </MDBNavItem>
                        <MDBNavItem>
                            <MDBNavLink className="waves-effect waves-light" to="/login/">
                                Log in <MDBIcon icon="sign-in-alt" />
                            </MDBNavLink>
                        </MDBNavItem>
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
                                            <NavLink to='/profile/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.profile" defaultMessage='Profile' /></NavLink>
                                        </div>
                                        <div>
                                            <NavLink to='/referral/' style={{ textDecoration: 'none' }}><FormattedMessage id="nav.referral" defaultMessage='Refer new user' /></NavLink>
                                        </div>
                                        <div>
                                            <NavLink to='/'
                                                style={{ textDecoration: 'none' }}
                                                onClick={() => {
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
                    </MDBNavbarNav>
                </MDBCollapse>
            </MDBNavbar>
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

export default withRouter(connect(mapStateToProps, { logout, handle_search, setLanguage })(TopNavbar));