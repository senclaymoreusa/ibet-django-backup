import React, { Component } from 'react';
import Navigation from "./navigation";
import axios from 'axios';
import { connect } from 'react-redux';
import { authCheckState } from '../actions';

class Home extends Component {
  state = {
    books: [],
    authors: [],
    bookinstance: []
  }  
  componentDidMount() {

    this.props.authCheckState();

    axios.get('http://127.0.0.1:8000/users/api/books/')
        .then(res => {
            this.setState({
                books: res.data
            });
        })

    axios.get('http://127.0.0.1:8000/users/api/authors/')
        .then(res => {
            this.setState({
              authors: res.data
            });
        })

    axios.get('http://127.0.0.1:8000/users/api/bookinstance/')
        .then(res => {
            this.setState({
              bookinstance: res.data
            });
        })
    }

    render() {

      const books = this.state.books
      const bookinstance = this.state.bookinstance
      const authors = this.state.authors
      var count = 0
      bookinstance.map(item => {
        if (item.status === 'a'){
          count += 1
        }
      })
      return (
        <div className="rows">
          <div> 
            <Navigation />
          </div>

          <div> 
              <h1> Claymore </h1>
              <h3> Local Library Home </h3>
              <div> The library has the following record counts: </div>
              <div> Books: {books.length} </div>
              <div> Copies: {bookinstance.length} </div>
              <div> Copies available: {count} </div>
              <div> Authors: {authors.length} </div>
          </div>
         
        </div>
      );
    }
  }

  
  export default connect(null, {authCheckState})(Home);