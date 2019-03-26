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
    notices: [],
  }
  
  componentDidMount() {

    this.props.authCheckState()
    axios.get(API_URL + 'users/api/notice-message', config)
    .then(res => {
      // console.log(res);
      this.setState({notices: res.data});
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