import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import { game_type } from '../actions';
import { connect } from 'react-redux';
import { FormattedMessage } from 'react-intl';
import  TopNavbar from "./top_navbar";
import '../css/game_type.css';

class Game_Type extends Component {

    type_change(text){
        this.props.game_type(text);
    }

    render() {
      return (
        <div>
          
            <TopNavbar />
          
          <div className='row'>

            <div className='type'>
                <NavLink to='/game_list/Sports' style={{ textDecoration: 'none' }}>
                    <div className='title-game'> 
                        <FormattedMessage id="games_type.sports" defaultMessage='Sports' />
                    </div>
                    <br/>
                    <img src="http://localhost:8000/media/game_image/soccer.jpg" height = '100' width = '150' alt='Not available' ></img>
                </NavLink>
                
            </div>

            <div className='type'>
                <NavLink to='/game_list/Casino' style={{ textDecoration: 'none' }} >
                    <div className='title-game'> 
                        <FormattedMessage id="games_type.casino" defaultMessage='Casino' />
                    </div>
                    <br/>
                    <img src="http://localhost:8000/media/game_image/casino.jpg" height = '100' width = '150' alt='Not available' ></img>
                </NavLink>
                
            </div>

            <div className='type'>
                <NavLink to='/game_list/Poker' style={{ textDecoration: 'none' }} >
                    <div className='title-game'> 
                        <FormattedMessage id="games_type.poker" defaultMessage='Poker' />
                    </div>
                    <br/>
                    <img src="http://localhost:8000/media/game_image/poker.jpg" height = '100' width = '150' alt='Not available' ></img>
                </NavLink>
                
            </div>

            <div className='type'> 
                <NavLink to='/game_list/Guide' style={{ textDecoration: 'none' }} >
                    <div className='title-game'> 
                         <FormattedMessage id="games_type.guide" defaultMessage='Guide' />
                    </div>
                    <br/>
                    <img src="http://localhost:8000/media/game_image/guide.png" height = '100' width = '150' alt='Not available' ></img>
                </NavLink>
                
            </div>

          </div>
        </div>
      );
    }
  }

  export default connect(null, {game_type})(Game_Type);