import React, { Component } from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { FormattedMessage } from 'react-intl';
import Navigation from "./navigation";
import { game_detail } from '../actions';
import { config } from '../util_config';



const API_URL = process.env.REACT_APP_REST_API;
class Game_List extends Component {

    state = {
        games: []
    }

    componentDidMount() {

        const { term } = this.props.match.params;
        // console.log(this.props.match.params);
        // const game_type = localStorage.getItem('game_type');
        var URL = API_URL + 'users/api/games/?' + term;
        axios.get(URL, config)
          .then(res => {
            this.setState({
              games: res.data
          });
        });
    }

    render() {
      const games = this.state.games;
      return (
        <div className="rows">
          <div>
            <Navigation />
          </div>
          <div>
          <h1><FormattedMessage id="games_list.title" defaultMessage='Game List' /></h1>
            {
              games.map(item => {
                  if (this.props.lang === 'zh' && item.name_zh) {
                    return (
                      <div key={item.name}>
                        <NavLink to = {`/game_detail/id=${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                          }}> {item.name_zh} </NavLink>
                        <br/>
                        <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                      </div>
                    )
                  }
                  else if (this.props.lang === 'fr' && item.name_fr) {
                    return (
                      <div key={item.name}>
                        <NavLink to = {`/game_detail/id=${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                          }}> {item.name_fr} </NavLink>
                        <br/>
                        <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                      </div>
                    )
                  }
                  else {
                    return (
                      <div key={item.name}>
                        <NavLink to = {`/game_detail/id=${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                          }}> {item.name} </NavLink>
                        <br/>
                        <img src={item.image} height = "100" width="100" alt = 'Not available'/>
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
        game_type: state.general.game_type,
        lang: state.language.lang
    }
}
  
export default connect(mapStateToProps, { game_detail })(Game_List);