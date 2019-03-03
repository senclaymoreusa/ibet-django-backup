import React, { Component } from 'react';
import Navigation from "./navigation";
import axios from 'axios';
import { connect } from 'react-redux';
import { authCheckState } from '../actions';
import { FormattedMessage } from 'react-intl';



const API_URL = process.env.REACT_APP_REST_API

class Home extends Component {
  state = {
    books: [],
    authors: [],
    bookinstance: []
  }  
  componentDidMount() {
    
    this.props.authCheckState()

    axios.get(API_URL + 'users/api/books/')
        .then(res => {
            this.setState({
                books: res.data
            });
        })

    axios.get(API_URL + 'users/api/authors/')
        .then(res => {
            this.setState({
              authors: res.data
            });
        })

    axios.get(API_URL + 'users/api/bookinstance/')
        .then(res => {
            this.setState({
              bookinstance: res.data
            });
        })
    }

    render() {

      const books = this.state.books;
      const bookinstance = this.state.bookinstance;
      const authors = this.state.authors;
      var count = 0;
      bookinstance.map(item => {
        if (item.status === 'a'){
          count += 1;
        }
      })
      return (
        <div className="rows">
          <div> 
            <Navigation />
          </div>

          <div> 
              <h1> <FormattedMessage id="home.title" defaultMessage='Claymore' /></h1>
              <h3> <FormattedMessage id="home.subtitle" defaultMessage='Local Library Home' /></h3>
              <div> <FormattedMessage id="home.heading" defaultMessage='The library has the following record counts' /> :</div>
              <div> <FormattedMessage id="home.books" defaultMessage='Books' />: {books.length} </div>
              <div> <FormattedMessage id="home.copies" defaultMessage='Copies' />: {bookinstance.length} </div>
              <div> <FormattedMessage id="home.copies_available" defaultMessage='Copies available' />: {count} </div>
              <div> <FormattedMessage id="home.authors" defaultMessage='Authors' />: {authors.length} </div>
          </div>
         
        </div>
      );
    }
  }

  
  export default connect(null, {authCheckState})(Home);