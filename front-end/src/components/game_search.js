import React, { Component } from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { game_detail } from '../actions'
import { config } from '../util_config';
import TopNavbar from './top_navbar';
import { FormattedMessage } from 'react-intl';
import ScrollMenu from 'react-horizontal-scrolling-menu';
import '../css/game_search.css';


const MenuItem = ({name, selected, image, pk, name_zh, name_fr, language}) => {
    if (language === 'zh' && name_zh){
      return (
        <div key={name} className='menu-item'>
          <NavLink to = {`/game_detail/${pk}`} style={{ textDecoration: 'none' }}> 
            {name_zh} 
            <br/>
            <img src={image} height = "150" width="150" alt = 'Not available'/>
          </NavLink>
        </div>
      )
    }else if (language === 'fr' && name_fr) {
      return (
        <div key={name} className='menu-item'>
        <NavLink to = {`/game_detail/${pk}`} style={{ textDecoration: 'none' }}> 
          {name_fr} 
          <br/>
          <img src={image} height = "150" width="150" alt = 'Not available'/>
        </NavLink>
      </div>
      )
    }else{
      return (
      <div className='menu-item'>
        <NavLink to = {`/game_detail/${pk}`} style={{ textDecoration: 'none' }} >
          {name}
          <br/>
          <img src={image} height = "150" width="150" alt = 'Not available'/>
        </NavLink>
      </div>
      )
    }
  };
   

const Menu = (list, language) =>
    list.map(item => {
      
    const {name} = item;
    const {image} = item;
    const {pk} = item;
    const {name_zh} = item;
    const {name_fr} = item;
   
    return <MenuItem name = {name} key = {name} image = {image} pk = {pk} name_zh = {name_zh} name_fr ={name_fr} language={language} />;
});
 
 
const Arrow = ({ text, className }) => {
  return (
    <div
      className={className}
    >{text}</div>
  );
};
 
 
const ArrowLeft = Arrow({ text: '<', className: 'arrow-prev' });
const ArrowRight = Arrow({ text: '>', className: 'arrow-next' });
 

const API_URL = process.env.REACT_APP_REST_API;

class Game_Search extends Component {
    constructor(props){
        super(props);
        this.state = { games: [], loading: true };
        // this.onInputChange = this.onInputChange.bind(this);
        // this.onFormSubmit = this.onFormSubmit.bind(this);
    }

    async componentWillReceiveProps(props) {
        // console.log('componentWillReceiveProps');

        const { term } = props.match.params;
        // console.log(props.match.params);
        // const token = localStorage.getItem('search_term');
        await this.searchGame(term);
       

        // if (term){
        //     var temp = [];
        //     var URL = API_URL + 'users/api/games/?' + term;
        //     await axios.get(URL, config)
        //     .then(res => {
        //           temp = res.data;
        //     })
        //   this.setState({games: temp});
        // }
        // this.setState({loading: false});
    }

    async componentDidMount() {

        const { term } = this.props.match.params;
        // console.log(this.props.match.params);

        await this.searchGame(term);
        // if (term){
        //     var temp = [];
        //     var URL = API_URL + 'users/api/games/?' + term;
        //     await axios.get(URL, config)
        //     .then(res => {
        //           temp = res.data;
        //     })
        //   this.setState({games: temp});
        // }
        // this.setState({loading: false});
    }

    searchGame = async (term) => {
        if (term){
            var temp = [];
            var URL = API_URL + 'users/api/games/?term=' + term;
            await axios.get(URL, config)
            .then(res => {
                temp = res.data;
            })
          this.setState({games: temp});
          this.setState({game_to_render: Menu(this.state.games, this.props.lang)})
        }
        this.setState({loading: false});
    }

    // onInputChange(event){
    //     this.setState({term: event.target.value});
    // }

    // onFormSubmit(event){
    //     event.preventDefault();
    //     // localStorage.setItem('search_term', this.state.term);
    //     // const token = localStorage.getItem('search_term'); 
    //     // this.fetch_game(this.state.term);
    //     // this.setState({ term: '' });
    // }

    render() {
      var games = this.state.games;

      const menu = this.state.game_to_render;

      return (
        <div>

            <TopNavbar />

            <div className='game-container'> 
              <ScrollMenu
                data={menu}
                arrowLeft={ArrowLeft}
                arrowRight={ArrowRight}
                hideArrows={true}
                hideSingleArrow={true}
                dragging={false}
                wheel={false}
                alignCenter={false}
              />
            </div>

            {
              games.length === 0 && this.state.loading === false?
              <div><FormattedMessage id="games_search.not_found" defaultMessage='No games matching your search' /></div>
              :
              <div> </div>
            }

        </div>
      )
    }
}

const mapStateToProps = (state) => {
    return {
        token: state.general.term,
        isAuthenticated: state.auth.token !== null,
        lang: state.language.lang
    }
}
  
export default connect(mapStateToProps, { game_detail })(Game_Search);