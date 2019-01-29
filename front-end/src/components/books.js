import React, { Component } from 'react';
import axios from 'axios';
import Navigation from "./navigation";

class Books extends Component {

    state = {
        books: []
    }

    componentDidMount() {
        axios.get('http://127.0.0.1:8000/users/api/books/')
            .then(res => {
                this.setState({
                    books: res.data
                });
            })
    }

    render() {

      const books = this.state.books
      return (
        <div className="rows">
          <div>
            <Navigation />
          </div>
          <div style={{marginLeft: 10}}>
            <h1> Book List </h1>
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