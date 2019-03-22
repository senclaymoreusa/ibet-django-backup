import React, { Component } from 'react';
import Navigation from "./navigation";
import { connect } from 'react-redux';
import { authCheckState } from '../actions';
import { FormattedMessage } from 'react-intl';
import Marquee from "react-smooth-marquee";
import axios from 'axios';
import { config } from '../util_config';
import moment from 'moment';

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
        let startTime = moment(notice.start_time);
        startTime = startTime.format('MM/DD/YYYY h:mm a');
        let endTime = moment(notice.end_time);
        endTime = endTime.format('MM/DD/YYYY h:mm a');
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
          { this.state.noticeMessage.length > 0 ? 
          <div>
          <Marquee>{this.state.noticeMessage}</Marquee>
          </div>
          : ''
          } 
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