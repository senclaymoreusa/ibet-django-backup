import React, { Component } from 'react';
import { connect } from 'react-redux';
import TopNavbar from "./top_navbar";
import axios from 'axios';
import { config } from '../util_config';
import { FormattedMessage } from 'react-intl';

const API_URL = process.env.REACT_APP_REST_API;


class Game_Detail extends Component {
  
  state = {
    game: {},
  }

  componentDidMount() {
    const { id } = this.props.match.params;
    axios.get(API_URL + `users/api/games-detail/?id=${id}`, config)
    .then(res => {
      let data = res.data[0];
      data.categoryName = data.category_id.name;
      this.setState({game: data});
    })

  }

  render() {
    const game = this.state.game;
    if (this.props.lang === 'zh') {
      if (game.name_zh) {
        game._name = game.name_zh;
      } else {
        game._name = game.name;
      }
      if (game.description_zh) {
        game._description = game.description_zh;
      } else {
        game._description = game.description;
      }
      
    } else if (this.props.lang === 'fr') {
      if (game.name_fr) {
        game._name = game.name_fr;
      } else {
        game._name = game.name;
      }
      if (game.description_fr) {
        game._description = game.description_fr;
      } else {
        game._description = game.description;
      }
    } else {
      game._name = game.name;
      game._description = game.description;
    }
   
    
    return(
      <div>
          <TopNavbar />
        <div>
          <h1><FormattedMessage id="game_detail.title" defaultMessage='Game Details' /></h1>
          
          <div><b><FormattedMessage id="game_detail.name" defaultMessage='name: ' /></b>{game._name}</div>
          <br/>
          <div><b><FormattedMessage id="game_detail.category" defaultMessage='category: ' /></b>{game.categoryName}</div>
          <br/>
          <div><b><FormattedMessage id="game_detail.startTime" defaultMessage='start_time: ' /></b>{game.start_time}</div>
          <br/>
          <div><b><FormattedMessage id="game_detail.endTime" defaultMessage='end_time: ' /></b>{game.end_time}</div>
          <br/>
          <div><b><FormattedMessage id="game_detail.opponent1" defaultMessage='opponent1: ' /></b>{game.opponent1}</div>
          <br/>
          <div><b><FormattedMessage id="game_detail.opponent2" defaultMessage='opponent2: ' /></b>{game.opponent2}</div>
          <br/>
          <div><b><FormattedMessage id="game_detail.description" defaultMessage='description: ' /></b>{game._description}</div>
          <br/>
          <img src={game.image} height = "100" width="100" alt = 'Not available'/>
        </div>

          <button style={{backgroundColor: 'white', border: '1px solid red', color: 'red'}} onClick={ () => {this.props.history.push('/')}}>
              <FormattedMessage id="login.back" defaultMessage='Back' />
          </button>
      </div>
    )
  }
}

const mapStateToProps = (state) => {
    return {
        game_detail: state.general.game_detail,
        lang: state.language.lang
    }
}

export default connect(mapStateToProps)(Game_Detail);