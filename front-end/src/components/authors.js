import React, { Component } from 'react';
import axios from 'axios';
import Navigation from "./navigation";

const API_URL = process.env.REACT_APP_REST_API

class Authors extends Component {

    state = {
        authors: []
    }

    componentDidMount() {
        axios.get(API_URL + 'users/api/authors/')
            .then(res => {
                this.setState({
                    authors: res.data
                });
            })
    }

    render() {
      const authors = this.state.authors
      return (
        <div className="rows">
          <div>
            <Navigation />
          </div>
        
          <div>
            <h1> Author List </h1>
            <div>
              {
                authors.map(item => {
                  return  <div key={item.first_name}> {item.first_name} {item.last_name} </div>
                })
              }
            </div>
          </div>
        </div>
      );
    }
  }
  
  export default Authors;