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
            <NavLink to='/game_list' style={{ textDecoration: 'none' }} onClick={()=>{this.type_change('Sports')}}><FormattedMessage id="games_type.sports" defaultMessage='Sports' /></NavLink>
            <br/>
            <NavLink to='/game_list' style={{ textDecoration: 'none' }} onClick={()=>{this.type_change('Casino')}}><FormattedMessage id="games_type.casino" defaultMessage='Casino' /></NavLink>
            <br/>
            <NavLink to='/game_list' style={{ textDecoration: 'none' }} onClick={()=>{this.type_change('Poker')}}><FormattedMessage id="games_type.poker" defaultMessage='Poker' /></NavLink>
            <br/>
            <NavLink to='/game_list' style={{ textDecoration: 'none' }} onClick={()=>{this.type_change('Guide')}}><FormattedMessage id="games_type.guide" defaultMessage='Guide' /></NavLink>
          </div>
        </div>
      );
    }
  }

  export default connect(null, {game_type})(Game_Type);