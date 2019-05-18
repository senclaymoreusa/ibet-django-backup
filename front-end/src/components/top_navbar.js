import React from 'react'; import PropTypes from 'prop-types';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import InputBase from '@material-ui/core/InputBase';
import MenuItem from '@material-ui/core/MenuItem';
import Menu from '@material-ui/core/Menu';
import { fade } from '@material-ui/core/styles/colorManipulator';
import { withStyles } from '@material-ui/core/styles';
import MenuIcon from '@material-ui/icons/Menu';
import SearchIcon from '@material-ui/icons/Search';
import PersonAdd from '@material-ui/icons/PersonAdd';
import Person from '@material-ui/icons/Person';
import Input from '@material-ui/icons/Input';
import Language from '@material-ui/icons/Language';

import MoreIcon from '@material-ui/icons/MoreVert';
import Tooltip from '@material-ui/core/Tooltip';
import Button from '@material-ui/core/Button';

import { FormattedMessage } from 'react-intl';
import { NavLink, withRouter } from 'react-router-dom';
import { connect } from 'react-redux';
import { logout, handle_search, setLanguage } from '../actions';

import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import AccountMenu from './account_menu';

import ClickAwayListener from '@material-ui/core/ClickAwayListener';
import Grow from '@material-ui/core/Grow';
import Paper from '@material-ui/core/Paper';
import Popper from '@material-ui/core/Popper';
import ButtonBase from '@material-ui/core/ButtonBase';


import Flag from 'react-flagkit';

const styles = theme => ({
    root: {
        width: '100%',
    },
    list: {
        width: 250,
    },
    subMenu: {
        width: '99%',
        marginTop: 15
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
        backgroundColor: fade(theme.palette.common.black, 0.15),
        '&:hover': {
            backgroundColor: fade(theme.palette.common.black, 0.25),
        },
        marginRight: theme.spacing.unit * 2,
        marginLeft: 0,
        marginTop: 5,
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
        color: 'black'
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
        color: 'white'
    },
    subbutton: {
        margin: theme.spacing.unit
    },
    nested: {
        paddingLeft: theme.spacing.unit * 4
    },
    image: {
        position: 'relative',
        height: 200,
        [theme.breakpoints.down('xs')]: {
            width: '100% !important', // Overrides inline-style
            height: 100,
        },
        '&:hover, &$focusVisible': {
            zIndex: 1,
            '& $imageBackdrop': {
                opacity: 0.15,
            },
            '& $imageMarked': {
                opacity: 0,
            },
            '& $imageTitle': {
                border: '4px solid currentColor',
            },
        },
    },
    focusVisible: {},
    imageButton: {
        position: 'absolute',
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: theme.palette.common.white,
    },
    imageSrc: {
        position: 'absolute',
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
        backgroundSize: 'cover',
        backgroundPosition: 'center 40%',
    },
    imageBackdrop: {
        position: 'absolute',
        left: 0,
        right: 0,
        top: 0,
        bottom: 0,
        backgroundColor: theme.palette.common.black,
        opacity: 0.4,
        transition: theme.transitions.create('opacity'),
    },
    imageTitle: {
        position: 'relative',
        padding: `${theme.spacing.unit * 2}px ${theme.spacing.unit * 4}px ${theme.spacing.unit + 6}px`,
    },
    imageMarked: {
        height: 3,
        width: 18,
        backgroundColor: theme.palette.common.white,
        position: 'absolute',
        bottom: -2,
        left: 'calc(50% - 9px)',
        transition: theme.transitions.create('opacity'),
    },
});

const images = [
    {
        url: '/images/sports_submenu/in_play.jpg',
        title: 'In-play',
        width: '18%',
    },
    {
        url: '/images/sports_submenu/football.jpg',
        title: 'Football',
        width: '18%',
    },
    {
        url: '/images/sports_submenu/basketball.jpg',
        title: 'Basketball',
        width: '18%',
    },
    {
        url: '/images/sports_submenu/tennis.jpg',
        title: 'Tennis',
        width: '18%',
    },
    {
        url: '/images/sports_submenu/horse_racing.jpg',
        title: 'Horse Racing',
        width: '18%',
    },
    {
        url: '/images/sports_submenu/all_sports.jpg',
        title: 'All Sports',
        width: '18%',
    },
];


export class TopNavbar extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            open: false,
            subMenuType: null,
            showSubMenu: false,

            anchorEl: null,
            showSportsMenu: false,
            showGamesMenu: false,
            lang: 'en',
            showTopPanel: false,
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

    handleSubMenuToggle = (param) => {
        if (this.state.subMenuType == param) {
            this.setState({ showSubMenu: false });
            this.setState({ subMenuType: null });
        } else {
            this.setState({ showSubMenu: false });
            this.setState({ showSubMenu: true });
            this.setState({ subMenuType: param });
        }
    };

    handleGamesToggle = () => {
        this.setState({ showSportsMenu: false });
        this.setState(state => ({ showGamesMenu: !state.showGamesMenu }));
    };

    handleClose = event => {
        if (this.anchorEl.contains(event.target)) { return; }

        this.setState({ showSubMenu: false });
        this.setState({ subMenuType: null });
    };

    submenuHandleChange = (event, submenu) => {
        this.setState({ submenu });
    };

    toggleSidePanel = (side, open) => () => {
        this.setState({
            [side]: open,
        });
    };

    handleLanguageMenuOpen = event => {
        this.setState({ anchorEl: event.currentTarget });
    };

    langMenuClicked = (event) => {
        this.setState({ anchorEl: null });
       this.setState({
            lang: event.currentTarget.dataset.myValue
        })
        //console.log(this.state.lang)
        this.changeLanguage(event.currentTarget.dataset.myValue);
    }

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
        const { showSubMenu } = this.state;
        const { subMenuType } = this.state;

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

        const gamesSubMenu = (
            <div style={{ display: 'flex' }}>
                <Button className={classes.subbutton} href="/game_type/" >Games</Button>
                <Button className={classes.subbutton}>Tournaments</Button>
                <div className={classes.grow} />
                <div className={classes.sectionDesktop}>
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
                </div>
            </div>
        );

        const sportsSubMenu = (
            <div style={{ display: 'flex' }}>
                {images.map(image => (
                    <ButtonBase
                        focusRipple
                        key={image.title}
                        className={classes.image}
                        focusVisibleClassName={classes.focusVisible}
                        style={{ width: image.width }}
                    >
                        <span
                            className={classes.imageSrc}
                            style={{ backgroundImage: `url(${window.location.origin + image.url})`, }}
                        />
                        <span className={classes.imageBackdrop} />
                        <span className={classes.imageButton}>
                            <Typography
                                component="span"
                                variant="subtitle1"
                                color="inherit"
                                className={classes.imageTitle}
                            >
                                {image.title}
                                <span className={classes.imageMarked} />
                            </Typography>
                        </span>
                    </ButtonBase>
                ))}
            </div>
        );


        let subMenuItem = (<div></div>);

        switch (subMenuType) {
            case 'games':
                subMenuItem = gamesSubMenu;
            case 'sports':
                subMenuItem = sportsSubMenu;
        }

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
                            <Button buttonRef={node => {
                                this.anchorEl = node;
                            }}
                                aria-owns={showSubMenu ? 'menu-list-grow' : undefined}
                                aria-haspopup="true"
                                onClick={() => this.handleSubMenuToggle('sports')} className={classes.button}>
                                Sports
                            </Button>
                            <Popper open={showSubMenu} anchorEl={this.anchorEl} transition disablePortal className={classes.subMenu}>
                                {({ TransitionProps, placement }) => (
                                    <Grow
                                        {...TransitionProps}
                                        id="menu-list-grow"
                                        style={{ transformOrigin: placement === 'bottom' ? 'center top' : 'center bottom' }}
                                    >
                                        <Paper>
                                            <ClickAwayListener onClickAway={this.handleClose}>
                                                {subMenuItem}
                                            </ClickAwayListener>
                                        </Paper>
                                    </Grow>
                                )}
                            </Popper>
                            <Button className={classes.button} href='/game_type/'>
                                Games
                            </Button>
                            <Button className={classes.button}>
                                Live Casino
                            </Button>
                            <Button className={classes.button}>
                                Lottery
                            </Button>
                            
                        </div>

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
                                    >
                                        <MenuItem onClick={this.langMenuClicked} data-my-value={'en'}>
                                            <ListItemIcon className={classes.icon}>
                                                <Flag country="US" />
                                            </ListItemIcon>
                                            <ListItemText classes={{ primary: classes.primary }} inset primary="English" />
                                        </MenuItem>
                                        <MenuItem onClick={this.langMenuClicked} data-my-value={'zh-hans'}>
                                            <ListItemIcon className={classes.icon}>
                                                <Flag country="CN" />
                                            </ListItemIcon>
                                            <ListItemText classes={{ primary: classes.primary }} inset primary="簡體中文" />
                                        </MenuItem>
                                        <MenuItem onClick={this.langMenuClicked} data-my-value={'fr'}><ListItemIcon className={classes.icon}>
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
                                            <AccountMenu />
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
                                        value={this.state.lang}
                                        onChange={this.langMenuClicked}
                                        anchorEl={anchorEl}
                                        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                                        transformOrigin={{ vertical: 'top', horizontal: 'right' }}
                                        open={Boolean(anchorEl)}
                                        onClose={this.handleLanguageMenuClose}
                                    >
                                        <MenuItem data-my-value={'en'} onClick={this.langMenuClicked}>
                                            <ListItemIcon className={classes.icon}>
                                                <Flag country="US" />
                                            </ListItemIcon>
                                            <ListItemText classes={{ primary: classes.primary }} inset primary="English" />
                                        </MenuItem>
                                        <MenuItem data-my-value={'zh-hans'} onClick={this.langMenuClicked}>
                                            <ListItemIcon className={classes.icon}>
                                                <Flag country="CN" />
                                            </ListItemIcon>
                                            <ListItemText classes={{ primary: classes.primary }} inset primary="簡體中文" />
                                        </MenuItem>
                                        <MenuItem data-my-value={'fr'} onClick={this.langMenuClicked}>
                                            <ListItemIcon className={classes.icon}>
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
                                    <AccountMenu />
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