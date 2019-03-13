import React, { Component } from 'react';
import { connect } from 'react-redux';
import Navigation from "./navigation";

class Game_Detail extends Component {

    render() {
      const game = JSON.parse(localStorage.getItem('game_detail'));
      return(
        <div className='rows'>
          <div>
            <Navigation />
          </div>
          <div>
            <h1> Game Details </h1>
            <div> <b>name:    </b>    {game.name}        </div>
            <br/>
            <div> <b>category:</b>    {game.name}        </div>
            <br/>
            <div> <b>start_time:</b>  {game.start_time}  </div>
            <br/>
            <div> <b>end_time:</b>    {game.end_time}    </div>
            <br/>
            <div> <b>opponent1:</b>   {game.opponent1}   </div>
            <br/>
            <div> <b>opponent2:</b>   {game.opponent2}   </div>
            <br/>
            <div> <b>description:</b> {game.description} </div>
            <br/>
            <img src={game.image} height = "100" width="100" alt = 'Not available'/>
          </div>
        </div>
      )
    }
}

const mapStateToProps = (state) => {
    return {
        game_detail: state.general.game_detail
    }
}

export default connect(mapStateToProps)(Game_Detail);