import React, { Component } from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import Navigation from "./navigation";
import { game_detail } from '../actions'

class Game_List extends Component {

    state = {
        games: []
    }

    componentDidMount() {
        axios.get('http://127.0.0.1:8000/users/api/games/')
            .then(res => {
                this.setState({
                  games: res.data
            });
        })
    }

    render() {
      const game_type = this.props.game_type
      const games = this.state.games
      return (
        <div className="rows">
          <div>
            <Navigation />
          </div>
          <div>
          <h1> Game List </h1>
            {
              games.map(item => {
                if(item.category_id.name === game_type){
                  return (
                    <div key={item.name}>
                      <NavLink to = '/game_detail' onClick={()=>{this.props.game_detail(item)}}> {item.name} </NavLink>
                      <br/>
                    </div>
                  )
                }
              })
            }
          </div>
        </div>
      );
    }
  }

const mapStateToProps = (state) => {
    return {
        game_type: state.general.game_type
    }
}
  
export default connect(mapStateToProps, { game_detail })(Game_List);