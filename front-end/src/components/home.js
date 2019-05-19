import React, { Component } from 'react';
import Footer from "./footer";
import TopNavbar from "./top_navbar";
import { connect } from 'react-redux';
import { authCheckState } from '../actions';
import { FormattedMessage } from 'react-intl';
import Marquee from "react-smooth-marquee";
import axios from 'axios';
import { config } from '../util_config';
import moment from 'moment';
import { NavLink } from 'react-router-dom';
import '../css/home.css';


const API_URL = process.env.REACT_APP_REST_API;

var height = window.innerHeight

export class Home extends Component {

  state = {
    notices: [],
    sports: [],
    casino: [],
    poker: [],
    ready: false
  }

  async componentDidMount() {

    this.props.authCheckState()
    axios.get(API_URL + 'operation/api/notice-message', config)
      .then(res => {
        //   console.log(res);
        this.setState({ notices: res.data });
      })

    var URL = API_URL + 'users/api/games/?term=Sports';

    await axios.get(URL, config)
      .then(res => {
        this.setState({ sports: res.data.slice(0, 3) });
      })

    URL = API_URL + 'users/api/games/?term=Casino';

    await axios.get(URL, config)
      .then(res => {
        this.setState({ casino: res.data.slice(0, 3) });
      })

    URL = API_URL + 'users/api/games/?term=Poker';

    await axios.get(URL, config)
      .then(res => {
        this.setState({ poker: res.data.slice(0, 3) });
      })

    this.setState({ ready: true })

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
        <TopNavbar style={{zIndex: '100'}} />
        
        {noticeStr && <div style={{ overflowX: 'hidden', zIndex: 0 }}><Marquee >{noticeStr}</Marquee></div>}

        {
          this.state.ready &&
          <div className='games' style={{ marginTop: height * 0.1 }}>
            <FormattedMessage id="home.sports" defaultMessage='Most Popular Sports' />
          </div>
        }

        <div className="rows" >
          {
            this.state.ready && this.state.sports.map(item => {
              return (
                  <div key={item.name} className='each-game' >
                    <NavLink to = {`/game_detail/${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                        }}> {item.name} </NavLink>
                    <br/>
                    <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                  </div>
                )
            })
          }
        </div>


        {
          this.state.ready &&
          <div className='poker' style={{ marginTop: height * 0.1 }}>
            <FormattedMessage id="home.poker" defaultMessage='Most Popluar Poker' />
          </div>
        }

        <div className="rows" >
          {
            this.state.ready && this.state.poker.map(item => {
              return (
                  <div key={item.name} className='each-game'>
                    <NavLink to = {`/game_detail/${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                        }}> {item.name} </NavLink>
                    <br/>
                    <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                  </div>
                )
            })
          }
        </div>

        {
          this.state.ready &&
          <div className='casino' style={{ marginTop: height * 0.1 }}>
            <FormattedMessage id="home.casino" defaultMessage='Most Popluar Casino' />
          </div>
        }

        <div className="rows" >
          {
            this.state.ready && this.state.casino.map(item => {
              return (
                  <div key={item.name} className='each-game'>
                    <NavLink to = {`/game_detail/${item.pk}`} style={{ textDecoration: 'none' }} onClick={()=>{
                        }}> {item.name} </NavLink>
                    <br/>
                    <img src={item.image} height = "100" width="100" alt = 'Not available'/>
                  </div>
                )
            })
          }
        </div>
          <Footer/>
      </div>

    );
  }
}

const mapStateToProps = (state) => {
  return {
    lang: state.language.lang
  }
}

export default connect(mapStateToProps, { authCheckState })(Home);