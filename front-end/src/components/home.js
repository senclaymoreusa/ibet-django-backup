import React, { Component } from 'react';
import Navigation from "./navigation";
import { connect } from 'react-redux';
import { authCheckState } from '../actions';
import { FormattedMessage } from 'react-intl';
import Marquee from "react-smooth-marquee";
import axios from 'axios';
import { config } from '../util_config';
import moment from 'moment';
import { NavLink } from 'react-router-dom';

const API_URL = process.env.REACT_APP_REST_API;


class Home extends Component {

  state = {
    notices: [],
    sports: [],
    casino: [],
    poker: []
  }
  
  async componentDidMount() {

    this.props.authCheckState()
    axios.get(API_URL + 'users/api/notice-message', config)
    .then(res => {
      // console.log(res);
      this.setState({notices: res.data});
    })

    var URL = API_URL + 'users/api/games/' + '?term=' + 'Sports'

    await axios.get(URL, config)
    .then(res => {
      this.setState({sports: res.data.slice(0, 3)})
    })

    var URL = API_URL + 'users/api/games/' + '?term=' + 'Casino'

    await axios.get(URL, config)
    .then(res => {
      this.setState({casino: res.data.slice(0, 3)})
    })

    var URL = API_URL + 'users/api/games/' + '?term=' + 'Poker'

    await axios.get(URL, config)
    .then(res => {
      this.setState({poker: res.data.slice(0, 3)})
    })
 
  }

  render() {

    let notices = this.state.notices;

    let noticeStr = '';
    notices.forEach(notice => {
      let startTime = moment(notice.start_time);
      startTime = startTime.format('MM/DD/YYYY h:mm a');
      let endTime = moment(notice.end_time);
      endTime = endTime.format('MM/DD/YYYY h:mm a');
      let i18nMessage = notice.message;
      if (this.props.lang === 'zh') {
        i18nMessage = notice.message_zh;
      } else if (this.props.lang === 'fr') {
        i18nMessage = notice.message_fr;
      } else {
        i18nMessage = notice.message;
      }
      let message = startTime + " ~ " + endTime + " " + i18nMessage;
      noticeStr += message;
      for (let i = 0; i < 20; i++) {
        noticeStr += "\u00A0";
      }
    });   

    return (
      <div >
        { noticeStr && <div style={{ overflowX: 'hidden' }}><Marquee >{noticeStr}</Marquee></div>}
        <div className="rows"> 
          <Navigation />
          <div> 
            <h1> <FormattedMessage id="home.title" defaultMessage='Claymore' /></h1>
          </div>
        </div>

        <h2 style={{marginLeft: '400px'}}> <FormattedMessage id="home.sports" defaultMessage='Most Popular Sports' /> </h2>
        <div className="rows" >
          {
            this.state.sports.map(item => {
              return (
                  <div key={item.name} style={{marginLeft: '300px'}}>
                    <NavLink to = {`/game_detail/${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                        }}> {item.name} </NavLink>
                    <br/>
                    <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                  </div>
                )
            })
          }
        </div>

        <h2 style={{marginLeft: '400px'}}> <FormattedMessage id="home.poker" defaultMessage='Most Popluar Poker' /> </h2>
        <div className="rows" >
          {
            this.state.poker.map(item => {
              return (
                  <div key={item.name} style={{marginLeft: '300px'}}>
                    <NavLink to = {`/game_detail/${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                        }}> {item.name} </NavLink>
                    <br/>
                    <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                  </div>
                )
            })
          }
        </div>

        <h2 style={{marginLeft: '400px'}}> <FormattedMessage id="home.casino" defaultMessage='Most Popluar Casino' /> </h2>
        <div className="rows" >
          {
            this.state.casino.map(item => {
              return (
                  <div key={item.name} style={{marginLeft: '300px'}}>
                    <NavLink to = {`/game_detail/${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                        }}> {item.name} </NavLink>
                    <br/>
                    <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                  </div>
                )
            })
          }
        </div>

      </div>
      
    );
  }
}

  const mapStateToProps = (state) => {
    return {
        lang: state.language.lang
    }
  }

  export default connect(mapStateToProps, {authCheckState})(Home);