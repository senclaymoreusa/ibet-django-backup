import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import { game_type } from '../actions';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import Navigation from "./navigation";

class Game_Type extends Component {

    type_change(text){
        this.props.game_type(text);
    }

    render() {
      return (
        <div className='rows'>
          <div>
            <Navigation />
          </div>
          <div>
            <h1> <FormattedMessage id="games_type.title" defaultMessage='Game Type' /></h1>
            <NavLink to='/game_list/Sports' style={{ textDecoration: 'none' }} onClick={()=>{
              // this.type_change('Sports')
              // localStorage.setItem('game_type', 'Sports');
              }}><FormattedMessage id="games_type.sports" defaultMessage='Sports' /></NavLink>
            <br/>
            <img src="http://localhost:8000/media/game_image/soccer.jpg" height = '100' width = '150' alt='Not available' ></img>
            <br/>
            <NavLink to='/game_list/Casino' style={{ textDecoration: 'none' }} onClick={()=>{
              // this.type_change('Casino')
              // localStorage.setItem('game_type', 'Casino');
              }}><FormattedMessage id="games_type.casino" defaultMessage='Casino' /></NavLink>
            <br/>
            <img src="http://localhost:8000/media/game_image/casino.jpg" height = '100' width = '150' alt='Not available' ></img>
            <br/>
            <NavLink to='/game_list/Poker' style={{ textDecoration: 'none' }} onClick={()=>{
              this.type_change('Poker')
              localStorage.setItem('game_type', 'Poker');
              }}><FormattedMessage id="games_type.poker" defaultMessage='Poker' /></NavLink>
            <br/>
            <img src="http://localhost:8000/media/game_image/poker.jpg" height = '100' width = '150' alt='Not available' ></img>
            <br/>
            <NavLink to='/game_list/Guide' style={{ textDecoration: 'none' }} onClick={()=>{
              this.type_change('Guide')
              localStorage.setItem('game_type', 'Guide');
              }}><FormattedMessage id="games_type.guide" defaultMessage='Guide' /></NavLink>
            <br/>
            <img src="http://localhost:8000/media/game_image/guide.png" height = '100' width = '150' alt='Not available' ></img>
          </div>
        </div>
      );
    }
  }

  export default connect(null, {game_type})(Game_Type);