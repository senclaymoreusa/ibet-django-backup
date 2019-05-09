import React, { Component } from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { game_detail } from '../actions'
import { config } from '../util_config';
import TopNavbar from './top_navbar';
import { FormattedMessage } from 'react-intl';
import '../css/game_search.css';


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
      return (
        <div>

            <TopNavbar />

            <div className='row'>

            {
              games.map(item => {
                if (this.props.lang === 'zh' && item.name_zh) {
                  return (
                    <div key={item.name} className="game_search">
                      <NavLink to = {`/game_detail/${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                        }}> {item.name_zh} </NavLink>
                      <br/>
                      <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                    </div>
                  )
                }
                else if (this.props.lang === 'fr' && item.name_fr) {
                  return (
                    <div key={item.name} className="game_search">
                      <NavLink to = {`/game_detail/${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                        }}> {item.name_fr} </NavLink>
                      <br/>
                      <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                    </div>
                  )
                }
                else {
                  return (
                    <div key={item.name} className="game_search">
                      <NavLink to = {`/game_detail/${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                        }}> {item.name} </NavLink>
                      <br/>
                      <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                    </div>
                  )
                }
              })
            }
            {
              games.length === 0 && this.state.loading === false?
              <div><FormattedMessage id="games_search.not_found" defaultMessage='No games matching your search' /></div>
              :
              <div> </div>
            }
            </div>
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