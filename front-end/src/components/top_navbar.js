import React from 'react'; import PropTypes from 'prop-types';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import InputBase from '@material-ui/core/InputBase';
import Badge from '@material-ui/core/Badge';
import MenuItem from '@material-ui/core/MenuItem';
import Menu from '@material-ui/core/Menu';
import { fade } from '@material-ui/core/styles/colorManipulator';
import { withStyles } from '@material-ui/core/styles';
import MenuIcon from '@material-ui/icons/Menu';
import SearchIcon from '@material-ui/icons/Search';
import AccountCircle from '@material-ui/icons/AccountCircle';
import PersonAdd from '@material-ui/icons/PersonAdd';
import Person from '@material-ui/icons/Person';
import Input from '@material-ui/icons/Input';
import Language from '@material-ui/icons/Language';
import MailIcon from '@material-ui/icons/Mail';
import PeopleOutline from '@material-ui/icons/PeopleOutline';
import DirectionsRun from '@material-ui/icons/DirectionsRun';

import NotificationsIcon from '@material-ui/icons/Notifications';
import MoreIcon from '@material-ui/icons/MoreVert';
import Tooltip from '@material-ui/core/Tooltip';
import Button from '@material-ui/core/Button';

import { FormattedMessage } from 'react-intl';
import { NavLink, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { logout, handle_search, setLanguage } from '../actions';

import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import Divider from '@material-ui/core/Divider';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import InboxIcon from '@material-ui/icons/MoveToInbox';

import Collapse from '@material-ui/core/Collapse';
import ExpandLess from '@material-ui/icons/ExpandLess';
import ExpandMore from '@material-ui/icons/ExpandMore';
import StarBorder from '@material-ui/icons/StarBorder';

import Flag from 'react-flagkit';

const styles = theme => ({
    root: {
        width: '100%',
    },
    list: {
        width: 250,
    },
    grow: {
        flexGrow: 1,
    },
    menuButton: {
        marginLeft: -12,
        marginRight: 20,
    },
    mobileLeftMenuButton: {
        marginLeft: -12,
        marginRight: 2,
    },
    mobileMenuButton: {
        marginLeft: 0,
        marginRight: -12,
    },
    title: {
        display: 'none',
        [theme.breakpoints.up('sm')]: {
            display: 'block',
        },
    },
    search: {
        position: 'relative',
        borderRadius: theme.shape.borderRadius,
        backgroundColor: fade(theme.palette.common.white, 0.15),
        '&:hover': {
            backgroundColor: fade(theme.palette.common.white, 0.25),
        },
        marginRight: theme.spacing.unit * 2,
        marginLeft: 0,
        width: '100%',
        [theme.breakpoints.up('sm')]: {
            marginLeft: theme.spacing.unit * 3,
            width: 'auto',
        },
    },
    searchIcon: {
        width: theme.spacing.unit * 9,
        height: '100%',
        position: 'absolute',
        pointerEvents: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white'
    },
    inputRoot: {
        color: 'inherit',
        width: '100%',
    },
    inputInput: {
        paddingTop: theme.spacing.unit,
        paddingRight: theme.spacing.unit,
        paddingBottom: theme.spacing.unit,
        paddingLeft: theme.spacing.unit * 10,
        transition: theme.transitions.create('width'),
        width: '100%',
        [theme.breakpoints.up('md')]: {
            width: 200,
        },
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
        margin: theme.spacing.unit,
        textTransform: 'capitalize',
        color: 'white'
    },
    nested: {
        paddingLeft: theme.spacing.unit * 4,
    },
});

const languages = [
    { value: 'en', label: 'English' },
    { value: 'zh-hans', label: '簡體中文' },
    { value: 'fr', label: 'Français' }
];

export class TopNavbar extends React.Component {

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

        this.onInputChange = this.onInputChange.bind(this);
        this.onFormSubmit = this.onFormSubmit.bind(this);

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

    onInputChange(event) {
        this.setState({ term: event.target.value });
    }

    onFormSubmit(event) {
        event.preventDefault();
        this.setState({ term: '' });
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

    toggleLanguageListItem = () => {
        this.setState(state => ({ showLangListItems: !state.showLangListItems }));
    };

    render() {
        const { anchorEl } = this.state;
        const { classes } = this.props;

        const leftMobileSideList = (
            <div className={classes.list}>
                <List>
                    <ListItem button component="a" href="/">
                        <ListItemIcon>
                            <Person />
                        </ListItemIcon>
                        <ListItemText>
                            <FormattedMessage id="nav.sports" defaultMessage='Sports' />
                        </ListItemText>
                    </ListItem>
                    <ListItem button component="a" href="/">
                        <ListItemIcon>
                            <Person />
                        </ListItemIcon>
                        <ListItemText>
                            <FormattedMessage id="nav.livecasino" defaultMessage='Live Casino' />
                        </ListItemText>
                    </ListItem>
                    <ListItem button component="a" href="/">
                        <ListItemIcon>
                            <Person />
                        </ListItemIcon>
                        <ListItemText>
                            <FormattedMessage id="nav.games" defaultMessage='Games' />
                        </ListItemText>
                    </ListItem>
                    <ListItem button component="a" href="/">
                        <ListItemIcon>
                            <Person />
                        </ListItemIcon>
                        <ListItemText>
                            <FormattedMessage id="nav.lottery" defaultMessage='Lottery' />
                        </ListItemText>
                    </ListItem>
                </List>
            </div>
        );

        const rightSideList = (
            <div className={classes.list}>
                <List>
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
                </List>
            </div>
        );

        const rightMobileSideList = (
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
        );

        return (
            <div className={classes.root}>
                <AppBar position="static" color="primary">
                    <Toolbar>
                        <div className={classes.sectionMobile}>
                            <IconButton
                                className={classes.mobileLeftMenuButton}
                                color="inherit"
                                aria-label="Open drawer"
                                onClick={this.toggleSidePanel('showLeftPanel', true)}>
                                <MenuIcon />
                            </IconButton>
                            <Drawer open={this.state.showLeftPanel} onClose={this.toggleSidePanel('showLeftPanel', false)}>
                                <div
                                    tabIndex={0}
                                    role="button"
                                    onClick={this.toggleSidePanel('showLeftPanel', false)}
                                    onKeyDown={this.toggleSidePanel('showLeftPanel', false)}
                                >
                                    {leftMobileSideList}
                                </div>
                            </Drawer>
                        </div>
                        <Typography className={classes.title} variant="h6" color="inherit" noWrap>
                            <Button href="/" className={classes.button}>
                                ibet
                        </Button>
                        </Typography>
                        <div className={classes.sectionDesktop}>
                            <Button href="#text-buttons" className={classes.button}>
                                Sports
                        </Button>
                            <Button href="/game_type/" className={classes.button}>
                                Games
                        </Button>
                            <Button href="/game_type/" className={classes.button}>
                                Live Casino
                        </Button>
                            <Button href="#text-buttons" className={classes.button}>
                                Lottery
                        </Button>
                        </div>
                        <form onSubmit={this.onFormSubmit} className="search">
                            <div className={classes.search}>
                                <div className={classes.searchIcon}>
                                    <NavLink to={`/game_search/${this.state.term}`} style={{ color: 'white' }}>
                                        <IconButton type="submit" color="inherit">
                                            <SearchIcon />
                                        </IconButton>
                                    </NavLink>
                                </div>
                                <InputBase
                                    placeholder="Search…"
                                    classes={{
                                        root: classes.inputRoot,
                                        input: classes.inputInput,
                                    }}
                                    value={this.state.term}
                                    onChange={this.onInputChange}
                                />
                            </div>
                        </form>
                        <div className={classes.grow} />
                        {
                            this.props.isAuthenticated || this.state.facebooklogin === 'true' ?
                                <div className={classes.sectionDesktop}>
                                    <Tooltip title="Change Language" placement="bottom">
                                        <IconButton
                                            className={classes.menuButton}
                                            aria-owns={Boolean(anchorEl) ? 'material-appbar' : undefined}
                                            aria-haspopup="true"
                                            onClick={this.handleLanguageMenuOpen}
                                            color="inherit"
                                        >
                                            <Language />
                                        </IconButton>
                                    </Tooltip>
                                    <Menu
                                        value={this.state.lang} onChange={this.langMenuClicked}
                                        anchorEl={anchorEl}
                                        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                                        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                                        open={Boolean(anchorEl)}
                                        onClose={this.handleLanguageMenuClose}
                                    >
                                        <MenuItem onClick={this.handleLanguageMenuClose} data-my-value={'en'}>
                                            <ListItemIcon className={classes.icon}>
                                                <Flag country="US" />
                                            </ListItemIcon>
                                            <ListItemText classes={{ primary: classes.primary }} inset primary="English" />
                                        </MenuItem>
                                        <MenuItem onClick={this.handleLanguageMenuClose} data-my-value={'zh-hans'}>
                                            <ListItemIcon className={classes.icon}>
                                                <Flag country="CN" />
                                            </ListItemIcon>
                                            <ListItemText classes={{ primary: classes.primary }} inset primary="簡體中文" />
                                        </MenuItem>
                                        <MenuItem onClick={this.handleLanguageMenuClose} data-my-value={'fr'}><ListItemIcon className={classes.icon}>
                                            <Flag country="FR" />
                                        </ListItemIcon>
                                            <ListItemText classes={{ primary: classes.primary }} inset primary="Français" />
                                        </MenuItem>
                                    </Menu>

                                    <Tooltip title="Account" placement="bottom">
                                        <IconButton
                                            className={classes.menuButton}
                                            color="inherit"
                                            aria-label="Open drawer"
                                            onClick={this.toggleSidePanel('showRightPanel', true)}>
                                            <Person />
                                        </IconButton>
                                    </Tooltip>
                                    <Drawer anchor="right" open={this.state.showRightPanel} onClose={this.toggleSidePanel('showRightPanel', false)}>
                                        <div
                                            tabIndex={0}
                                            role="button"
                                            onClick={this.toggleSidePanel('showRightPanel', false)}
                                            onKeyDown={this.toggleSidePanel('showRightPanel', false)}
                                        >
                                            {rightSideList}
                                        </div>
                                    </Drawer>
                                </div>
                                :
                                <div className={classes.sectionDesktop}>
                                    <Tooltip title="Change Language" placement="bottom">
                                        <IconButton
                                            aria-owns={Boolean(anchorEl) ? 'material-appbar' : undefined}
                                            aria-haspopup="true"
                                            onClick={this.handleLanguageMenuOpen}
                                            color="inherit"
                                        >
                                            <Language />
                                        </IconButton>
                                    </Tooltip>
                                    <Menu
                                        value={this.state.lang} onChange={this.langMenuClicked}
                                        anchorEl={anchorEl}
                                        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                                        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                                        open={Boolean(anchorEl)}
                                        onClose={this.handleLanguageMenuClose}
                                    >
                                        <MenuItem onClick={this.handleLanguageMenuClose} data-my-value={'en'}>
                                            <ListItemIcon className={classes.icon}>
                                                <Flag country="US" />
                                            </ListItemIcon>
                                            <ListItemText classes={{ primary: classes.primary }} inset primary="English" />
                                        </MenuItem>
                                        <MenuItem onClick={this.handleLanguageMenuClose} data-my-value={'zh-hans'}>
                                            <ListItemIcon className={classes.icon}>
                                                <Flag country="CN" />
                                            </ListItemIcon>
                                            <ListItemText classes={{ primary: classes.primary }} inset primary="簡體中文" />
                                        </MenuItem>
                                        <MenuItem onClick={this.handleLanguageMenuClose} data-my-value={'fr'}><ListItemIcon className={classes.icon}>
                                            <Flag country="FR" />
                                        </ListItemIcon>
                                            <ListItemText classes={{ primary: classes.primary }} inset primary="Français" />
                                        </MenuItem>
                                    </Menu>
                                    <Tooltip title="Signup" placement="bottom">
                                        <IconButton
                                            aria-owns={Boolean(anchorEl) ? 'material-appbar' : undefined}
                                            aria-haspopup="true"
                                            color="inherit"
                                            onClick={() => { this.props.history.push('/signup/') }}
                                        >
                                            <PersonAdd />
                                        </IconButton>
                                    </Tooltip>
                                    <Tooltip title="Login" placement="bottom">
                                        <IconButton
                                            aria-owns={Boolean(anchorEl) ? 'material-appbar' : undefined}
                                            aria-haspopup="true"
                                            color="inherit"
                                            onClick={() => { this.props.history.push('/login/') }}
                                        >
                                            <Input />
                                        </IconButton>
                                    </Tooltip>
                                </div>
                        }
                        <div className={classes.sectionMobile}>
                            <IconButton
                                className={classes.mobileMenuButton}
                                color="inherit"
                                aria-label="Open drawer"
                                onClick={this.toggleSidePanel('showRightPanel', true)}>
                                <MoreIcon />
                            </IconButton>
                            <Drawer anchor="right" open={this.state.showRightPanel} onClose={this.toggleSidePanel('showRightPanel', false)}>
                                <div
                                    tabIndex={0}
                                    role="button"
                                >
                                    {rightMobileSideList}
                                </div>
                            </Drawer>
                        </div>
                    </Toolbar>
                </AppBar>
            </div >
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

TopNavbar.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(styles)(withRouter(connect(mapStateToProps, { logout, handle_search, setLanguage })(TopNavbar)));