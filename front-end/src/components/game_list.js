import React, { Component } from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { FormattedMessage } from 'react-intl';
import TopNavbar from "./top_navbar";
import { game_detail } from '../actions';
import { config } from '../util_config';
import ScrollMenu from 'react-horizontal-scrolling-menu';
import '../css/game_list.css';

const MenuItem = ({name, selected, image, pk, name_zh, name_fr, language}) => {
    if (language === 'zh' && name_zh){
      return (
        <div key={name} className='menu-item'>
          <NavLink to = {`/game_detail/${pk}`} style={{ textDecoration: 'none' }}> 
            {name_zh} 
            <br/>
            <img src={image} height = "150" width="150" alt = 'Not available'/>
          </NavLink>
        </div>
      )
    }else if (language === 'fr' && name_fr) {
      return (
        <div key={name} className='menu-item'>
        <NavLink to = {`/game_detail/${pk}`} style={{ textDecoration: 'none' }}> 
          {name_fr} 
          <br/>
          <img src={image} height = "150" width="150" alt = 'Not available'/>
        </NavLink>
      </div>
      )
    }else{
      return (
      <div className='menu-item'>
        <NavLink to = {`/game_detail/${pk}`} style={{ textDecoration: 'none' }} >
          {name}
          <br/>
          <img src={image} height = "150" width="150" alt = 'Not available'/>
        </NavLink>
      </div>
      )
    }
  };
   

const Menu = (list, language) =>
    list.map(item => {
      
    const {name} = item;
    const {image} = item;
    const {pk} = item;
    const {name_zh} = item;
    const {name_fr} = item;
   
    return <MenuItem name = {name} key = {name} image = {image} pk = {pk} name_zh = {name_zh} name_fr ={name_fr} language={language} />;
});
 
 
const Arrow = ({ text, className }) => {
  return (
    <div
      className={className}
    >{text}</div>
  );
};
 
 
const ArrowLeft = Arrow({ text: '<', className: 'arrow-prev' });
const ArrowRight = Arrow({ text: '>', className: 'arrow-next' });

const API_URL = process.env.REACT_APP_REST_API;

class Game_List extends Component {

    state = {
        games: []
    }

    componentDidMount() {

        const { term } = this.props.match.params;
        // console.log(this.props.match.params);
        // const game_type = localStorage.getItem('game_type');
        var URL = API_URL + 'users/api/games/?term=' + term;
        axios.get(URL, config)
          .then(res => {
            this.setState({
              games: res.data
          });
          this.setState({game_to_render: Menu(this.state.games, this.props.lang)})
        });
    }

    render() {
      const games = this.state.games;

      const menu = this.state.game_to_render;

      return (
        <div>

            <TopNavbar />

            <div className='game-container'> 
              <ScrollMenu
                data={menu}
                arrowLeft={ArrowLeft}
                arrowRight={ArrowRight}
                hideArrows={true}
                hideSingleArrow={true}
                dragging={false}
                wheel={false}
                alignCenter={false}
              />
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