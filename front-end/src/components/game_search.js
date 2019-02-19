import React, { Component } from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { game_detail } from '../actions'

const API_URL = process.env.REACT_APP_REST_API

class Game_Search extends Component {
    constructor(props){
        super(props);
        this.state = { term: '', games: [] };
        this.onInputChange = this.onInputChange.bind(this);
        this.onFormSubmit = this.onFormSubmit.bind(this);
    }

    async componentDidMount() {
        if (this.props.token){
            var temp = []
            var URL = API_URL + 'users/api/games/' + '?term=' + this.props.token
            await axios.get(URL)
            .then(res => {
                  temp = res.data
            })
          this.setState({games: temp})
        }
    }

    fetch_game = async (text) => {
        var URL = API_URL + 'users/api/games/' + '?term=' + text
        var result = (await axios.get(URL)).data
        if (text){
            this.setState({games: result})
        }
    }

    onInputChange(event){
        this.setState({term: event.target.value});
    }

    onFormSubmit(event){
        event.preventDefault();
        this.fetch_game(this.state.term);
        this.setState({ term: '' });
    }

    render() {
      var games = this.state.games
      return (
        <div className="rows" >
            <div style={{marginTop: 30, marginRight: 50}}>
                <div>
                    <NavLink to='/' style={{ textDecoration: 'none' }}> Home </NavLink>
                </div>
                <div>
                    <NavLink to='/books/' style={{ textDecoration: 'none' }}> All books </NavLink>
                </div>
                <div>
                    <NavLink to='/authors/' style={{ textDecoration: 'none' }}> All authors </NavLink>
                </div>
                <div>
                    <NavLink to='/game_type/' style={{ textDecoration: 'none' }}> All Games </NavLink>
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
                            Search 
                        </button>
                    </span>
                </form>

                {
                    this.props.isAuthenticated ?
                    <NavLink to = '/profile/' style={{ textDecoration: 'none' }}> Profile </NavLink>
                    :
                    <div> </div>
                }
                
                {
                    this.props.isAuthenticated ?
                    <div>
                        <NavLink to = '/' style={{ textDecoration: 'none' }} onClick={()=>{this.props.logout()}}> Logout </NavLink>
                    </div>
                    :
                    <div> 
                        <NavLink to='/login/' style={{ textDecoration: 'none' }}> Login </NavLink> 
                    </div>
                }
            </div>
            
            <div style={{marginLeft: 30, marginTop: 0}}>
              <h1> Searched games </h1>
              {
                games.map(item => {
                    return (
                        <div key={item.name}>
                          <NavLink to = '/game_detail' style={{ textDecoration: 'none' }} onClick={()=>{this.props.game_detail(item)}}> {item.name} </NavLink>
                          <br/>
                        </div>
                      )
                })
              }
              {
                  games.length === 0 ?
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