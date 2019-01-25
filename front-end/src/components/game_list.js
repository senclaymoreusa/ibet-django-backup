import React, { Component } from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import Navigation from "./navigation";

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
                  return <div key={item.name}> {item.name} </div>
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
  
export default connect(mapStateToProps)(Game_List);