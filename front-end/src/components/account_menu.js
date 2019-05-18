import React from 'react'; import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import PersonAdd from '@material-ui/icons/PersonAdd';
import Person from '@material-ui/icons/Person';
import Input from '@material-ui/icons/Input';
import Language from '@material-ui/icons/Language';
import Settings from '@material-ui/icons/Settings';
import PersonOutline from '@material-ui/icons/PersonOutline';
import BarChart from '@material-ui/icons/BarChart';
import CardGiftcard from '@material-ui/icons/CardGiftcard';
import Message from '@material-ui/icons/Message';
import TouchApp from '@material-ui/icons/TouchApp';
import AttachMoney from '@material-ui/icons/AttachMoney';

import PeopleOutline from '@material-ui/icons/PeopleOutline';
import DirectionsRun from '@material-ui/icons/DirectionsRun';

import { FormattedMessage } from 'react-intl';
import { withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { logout, handle_search, setLanguage, postLogout } from '../actions';

import List from '@material-ui/core/List';
import Divider from '@material-ui/core/Divider';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';

import Collapse from '@material-ui/core/Collapse';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import Button from '@material-ui/core/Button';
import FormControl from '@material-ui/core/FormControl';
import FormLabel from '@material-ui/core/FormLabel';
import Flag from 'react-flagkit';

const styles = theme => ({
    root: {
        width: '100%',
    },
    list: {
        width: 250,
    },
    sectionDesktop: {
        display: 'none',
        [theme.breakpoints.up('md')]: {
            display: 'flex',
        },
    },
    sectionMobile: {
        display: 'flex',
        [theme.breakpoints.up('md')]: {
            display: 'none',
        },
    },
    button: {
        width: '90%',
        margin: theme.spacing.unit,
        textTransform: 'capitalize'
    },
    nested: {
        paddingLeft: theme.spacing.unit * 4,
    },
    formControl: {
        margin: theme.spacing.unit * 3,
    },
});

export class AccountMenu extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            anchorEl: null,

            lang: 'en',
            showLeftPanel: false,
            showRightPanel: false,
            showLangListItems: false,
            term: '',
            facebooklogin: false,
            userID: "",
            name: "",
            email: "",
            picture: ""
        };


    }

    toggleSidePanel = (side, open) => () => {
        this.setState({
            [side]: open,
        });
    };

    handleLanguageMenuOpen = event => {
        this.setState({ anchorEl: event.currentTarget });
    };

    handleLanguageMenuClose = (ev) => {
        this.setState({ anchorEl: null });
        this.changeLanguage(ev.nativeEvent.target.dataset.myValue);
    };

    changeLanguage = (lang) => {
        this.props.setLanguage(lang)
            .then((res) => {
                // console.log("language change to:" + res.data);
            });
    };

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

    toggleLanguageListItem = () => {
        this.setState(state => ({ showLangListItems: !state.showLangListItems }));
    };

    render() {
        const { classes } = this.props;

        return (
            <div>
                <div className={classes.sectionDesktop}>
                    <div className={classes.list}>
                        <Button variant="contained" className={classes.button}>
                            Trade in
                        </Button>
                        <FormControl component="fieldset" className={classes.formControl}>
                            <FormLabel component="legend">Your Goodies</FormLabel>
                            <FormLabel component="legend">10 Free Spins on Starburst</FormLabel>
                        </FormControl>
                        <Divider />
                        <FormControl component="fieldset" className={classes.formControl}>
                            <FormLabel component="legend">Main wallet</FormLabel>
                            <FormLabel component="legend">Sportsbook A</FormLabel>
                            <FormLabel component="legend">Live Casino</FormLabel>
                            <FormLabel component="legend">Games</FormLabel>
                        </FormControl>
                        <Button variant="contained" color="primary" className={classes.button}>
                            Deposit
                        </Button>
                        <Button variant="contained" color="secondary" className={classes.button}>
                            Withdraw
                        </Button>
                        <List>
                            <Divider />
                            <ListItem button component="a" href="/">
                                <ListItemIcon>
                                    <AttachMoney />
                                </ListItemIcon>
                                <ListItemText>
                                    <FormattedMessage id="nav.fundmanagement" defaultMessage='Fund Management' />
                                </ListItemText>
                            </ListItem>
                            <ListItem button component="a" href="/">
                                <ListItemIcon>
                                    <TouchApp />
                                </ListItemIcon>
                                <ListItemText>
                                    <FormattedMessage id="nav.openbets" defaultMessage='Open Bets' />
                                </ListItemText>
                            </ListItem>
                            <ListItem button component="a" href="/">
                                <ListItemIcon>
                                    <Message />
                                </ListItemIcon>
                                <ListItemText>
                                    <FormattedMessage id="nav.messages" defaultMessage='Messages' />
                                </ListItemText>
                            </ListItem>
                            <ListItem button component="a" href="/">
                                <ListItemIcon>
                                    <CardGiftcard />
                                </ListItemIcon>
                                <ListItemText>
                                    <FormattedMessage id="nav.pointsrewards" defaultMessage='Points & Rewards' />
                                </ListItemText>
                            </ListItem>
                            <ListItem button component="a" href="/">
                                <ListItemIcon>
                                    <BarChart />
                                </ListItemIcon>
                                <ListItemText>
                                    <FormattedMessage id="nav.usageanalysis" defaultMessage='Usage Analysis' />
                                </ListItemText>
                            </ListItem>
                            <ListItem button component="a" href="/">
                                <ListItemIcon>
                                    <PersonOutline />
                                </ListItemIcon>
                                <ListItemText>
                                    <FormattedMessage id="nav.personaldetails" defaultMessage='Personal Details' />
                                </ListItemText>
                            </ListItem>
                            <ListItem button component="a" href="/">
                                <ListItemIcon>
                                    <Settings />
                                </ListItemIcon>
                                <ListItemText>
                                    <FormattedMessage id="nav.accountsettings" defaultMessage='Account Settings' />
                                </ListItemText>
                            </ListItem>
                            <Divider />
                            <ListItem button component="a" href="/profile/">
                                <ListItemIcon>
                                    <Person />
                                </ListItemIcon>
                                <ListItemText>
                                    <FormattedMessage id="nav.profile" defaultMessage='Profile' />
                                </ListItemText>
                            </ListItem>

                            <ListItem button component="a" href="/referral/">
                                <ListItemIcon>
                                    <PeopleOutline />
                                </ListItemIcon>
                                <ListItemText>
                                    <FormattedMessage id="nav.referral" defaultMessage='Refer new user' />
                                </ListItemText>
                            </ListItem>

                          
                            <Button variant="contained" className={classes.button} onClick={() => {
                                this.props.logout()
                                postLogout();
                            }}>
                                <FormattedMessage id="nav.logout" defaultMessage='Logout' />
                            </Button>
                        </List>
                    </div>
                </div>
                <div className={classes.sectionMobile}>
                    <div className={classes.list}>
                        <List>
                            {
                                this.props.isAuthenticated || this.state.facebooklogin === 'true' ?
                                    <div>
                                        <ListItem button component="a" href="/profile/">
                                            <ListItemIcon>
                                                <Person />
                                            </ListItemIcon>
                                            <ListItemText>
                                                <FormattedMessage id="nav.profile" defaultMessage='Profile' />
                                            </ListItemText>
                                        </ListItem>

                                        <ListItem button component="a" href="/referral/">
                                            <ListItemIcon>
                                                <PeopleOutline />
                                            </ListItemIcon>
                                            <ListItemText>
                                                <FormattedMessage id="nav.referral" defaultMessage='Refer new user' />
                                            </ListItemText>
                                        </ListItem>

                                        <ListItem onClick={() => {
                                            this.props.logout()
                                            window.location.reload()
                                        }}>
                                            <ListItemIcon>
                                                <DirectionsRun />
                                            </ListItemIcon>
                                            <ListItemText>
                                                <FormattedMessage id="nav.logout" defaultMessage='Logout' />
                                            </ListItemText>
                                        </ListItem>
                                    </div>
                                    :
                                    <div>
                                        <ListItem button component="a" href="/signup/">
                                            <ListItemIcon>
                                                <PersonAdd />
                                            </ListItemIcon>
                                            <ListItemText>
                                                <FormattedMessage id="nav.signup" defaultMessage='Signup' />
                                            </ListItemText>
                                        </ListItem>
                                        <ListItem button component="a" href="/login/">
                                            <ListItemIcon>
                                                <Input />
                                            </ListItemIcon>
                                            <ListItemText>
                                                <FormattedMessage id="nav.login" defaultMessage='Login' />
                                            </ListItemText>
                                        </ListItem>
                                    </div>
                            }
                            <div>
                                <Divider />
                                <ListItem button onClick={this.toggleLanguageListItem}>
                                    <ListItemIcon>
                                        <Language />
                                    </ListItemIcon>
                                    <ListItemText inset primary="Languages" />
                                    {this.state.showLangListItems ? <ExpandLess /> : <ExpandMore />}
                                </ListItem>
                                <Collapse in={this.state.showLangListItems} timeout="auto" unmountOnExit>
                                    <List component="div" disablePadding>
                                        <ListItem button className={classes.nested}>
                                            <ListItemIcon>
                                                <Flag country="US" />
                                            </ListItemIcon>
                                            <ListItemText inset primary="English" onClick={() => this.changeLanguage('en')} />
                                        </ListItem>
                                        <ListItem button className={classes.nested} onClick={() => this.changeLanguage('zh-hans')}>
                                            <ListItemIcon>
                                                <Flag country="CN" />
                                            </ListItemIcon>
                                            <ListItemText inset primary="簡體中文" />
                                        </ListItem>
                                        <ListItem button className={classes.nested}>
                                            <ListItemIcon>
                                                <Flag country="FR" />
                                            </ListItemIcon>
                                            <ListItemText inset primary="Français" onClick={() => this.changeLanguage('fr')} />
                                        </ListItem>
                                    </List>
                                </Collapse>
                            </div>
                        </List>
                    </div>
                </div>
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

AccountMenu.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(withRouter(connect(mapStateToProps, { logout, handle_search, setLanguage })(AccountMenu)));