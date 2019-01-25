import React, { Component } from 'react';
import axios from 'axios';
import Navigation from "./navigation";

class Authors extends Component {

    state = {
        authors: []
    }

    componentDidMount() {
        axios.get('http://127.0.0.1:8000/users/api/authors/')
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