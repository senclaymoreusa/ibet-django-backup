import React, { Component } from 'react';
import { FormattedMessage } from 'react-intl';
import axios from 'axios';
import Navigation from "./navigation";
import { config } from '../util_config';


const API_URL = process.env.REACT_APP_REST_API;

class Books extends Component {

    state = {
        books: []
    }

    componentDidMount() {
        axios.get(API_URL + 'users/api/books/', config)
            .then(res => {
                this.setState({
                    books: res.data
                });
            })
    }

    render() {

      const books = this.state.books;
      return (
        <div className="rows">
          <div>
            <Navigation />
          </div>
          <div style={{marginLeft: 10}}>
            <h1> <FormattedMessage id="books.title" defaultMessage='Book List' /></h1>
            {
              books.map(item => {
                return  <div key={item.title}> {item.title}  {item.author.first_name} {item.author.last_name}  </div>
              })
            }
          </div>
        </div>
      );
    }
  }

export default Books;