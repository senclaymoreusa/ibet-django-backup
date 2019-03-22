import React, { Component } from 'react';
import Navigation from "./navigation";
import { connect } from 'react-redux';
import { authCheckState } from '../actions';
import { FormattedMessage } from 'react-intl';
import Marquee from "react-smooth-marquee";
import axios from 'axios';
import { config } from '../util_config';

const API_URL = process.env.REACT_APP_REST_API;


class Home extends Component {

  state = {
    noticeMessage: '',
  }
  
  componentDidMount() {

    this.props.authCheckState()
    axios.get(API_URL + 'users/api/notice-message', config)
    .then(res => {
      // console.log(res);
      let data = res.data;
      let notices = '';
      data.forEach(notice => {
        let start_time = new Date(notice.start_time);
        let startTime = start_time.getFullYear() + "/" + start_time.getMonth()+1 + "/" + start_time.getDate() + " " + start_time.getHours() + ":" + start_time.getMinutes();
        let end_time = new Date(notice.end_time);
        let endTime = end_time.getFullYear() + "/" + end_time.getMonth()+1 + "/" + end_time.getDate() + " " + end_time.getHours() + ":" + end_time.getMinutes();
        let message = startTime + " ~ " + endTime + " " + notice.message;
        notices += message;
        for (let i = 0; i < 20; i++) {
          notices += "\u00A0";
        }
      });
      this.setState({noticeMessage: notices});
    })
 
  }

  render() {
      return (
        <div >
          <div>
          <Marquee>{this.state.noticeMessage}</Marquee>
          </div>
          <div className="rows"> 
            <Navigation />
            <div> 
              <h1> <FormattedMessage id="home.title" defaultMessage='Claymore' /></h1>
            </div>
          </div>
        </div>
        
      );
    }
  }

  export default connect(null, {authCheckState})(Home);