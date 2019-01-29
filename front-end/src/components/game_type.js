import React, { Component } from 'react';
import { NavLink } from 'react-router-dom';
import { game_type } from '../actions';
import { connect } from 'react-redux';
import Navigation from "./navigation";

class Game_Type extends Component {

    type_change(text){
        console.log(text)
        this.props.game_type(text);
    }

    render() {
      return (
        <div className='rows'>
          <div>
            <Navigation />
          </div>
          <div>
            <h1> Game Type </h1>
            <NavLink to='/game_list' onClick={()=>{this.type_change('Sports')}}> Sports </NavLink>
            <br/>
            <NavLink to='/game_list' onClick={()=>{this.type_change('Casino')}}> Casino </NavLink>
            <br/>
            <NavLink to='/game_list' onClick={()=>{this.type_change('Poker')}}> Poker </NavLink>
            <br/>
            <NavLink to='/game_list' onClick={()=>{this.type_change('Guide')}}> GUIDES </NavLink>
          </div>
        </div>
      );
    }
  }

  export default connect(null, {game_type})(Game_Type);