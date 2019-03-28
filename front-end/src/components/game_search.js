import React, { Component } from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { game_detail } from '../actions'
import { config } from '../util_config';

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
            var URL = API_URL + 'users/api/games/?' + term;
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
        <div className="rows" >
            <Navigation />
            <div style={{marginLeft: 30, marginTop: 0}}>
              <h1> Searched games </h1>
              {
                games.map(item => {
                    return (
                        <div key={item.name}>
                          <NavLink to = {`/game_detail/id=${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                              //this.props.game_detail(item)
                            //   localStorage.setItem('game_detail', JSON.stringify(item));
                              }}> {item.name} </NavLink>
                          <br/>
                          <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                        </div>
                      )
                })
              }
              {
                  games.length === 0 && this.state.loading === false?
                  <div> No games matching your search </div>
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
        isAuthenticated: state.auth.token !== null
    }
}
  
export default connect(mapStateToProps, { game_detail })(Game_Search);