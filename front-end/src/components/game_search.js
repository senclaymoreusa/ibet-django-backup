import React, { Component } from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import { NavLink } from 'react-router-dom';
import { game_detail } from '../actions'

var parent_categories = ['sports', 'casino', 'poker', 'guide']
var sub_categories = ['football','basketball', 'soccer', 'hockey', 'golf', 'tennis', 'baseball',]


class Game_Search extends Component {

    constructor(props){
        super(props);
        this.state = { term: '', games: [] };
        this.onInputChange = this.onInputChange.bind(this);
        this.onFormSubmit = this.onFormSubmit.bind(this);
    }

    async componentDidMount() {
        if (this.props.token){
            var temp = []
            await axios.get('http://127.0.0.1:8000/users/api/games/')
            .then(res => {
                  temp = res.data
            })

            var result = []
            if (parent_categories.includes(this.props.token.toLowerCase())){
                temp.map(item => {
                    if (item.category_id.name.toLowerCase() === this.props.token.toLowerCase() ){
                        result.push(item);
                    }
                })
            }else if(sub_categories.includes(this.props.token.toLowerCase())){
                temp.map(item => {
                    if (item.category.toLowerCase() === this.props.token.toLowerCase() ){
                        result.push(item);
                    }
                })
            }
            else{
                temp.map(item => {
                    if ( item.name.toLowerCase().includes(this.props.token.toLowerCase())){
                        result.push(item);
                    }
                })
            }
            
          this.setState({games: result})
        }
    }

    fetch_game = async (text) => {
        try{
          var data = (await axios.get('http://127.0.0.1:8000/users/api/games/')).data
          var result = []

          if (parent_categories.includes(text.toLowerCase())){
            data.map(item => {
                if (item.category_id.name.toLowerCase() === text.toLowerCase() ){
                    result.push(item);
                }
            })
          }else if(sub_categories.includes(text.toLowerCase())){
            data.map(item => {
                if (item.category.toLowerCase() === text.toLowerCase() ){
                    result.push(item);
                }
            })
        }else{
            data.map(item => {
                if ( item.name.toLowerCase().includes(text.toLowerCase())){
                    result.push(item);
                }
              })
          }
          
          if (text){
            this.setState({games: result})
          }
          {/*
          else{
              this.setState({games: [{name: "No result available"}]})
          }
          */}
          
          return result
        } catch(err){
          console.log(err)
        }
    }

    onInputChange(event){
        this.setState({term: event.target.value});
    }

    onFormSubmit(event){
        event.preventDefault();
        this.fetch_game(this.state.term);
    }

    render() {
      
      var games = this.state.games
      return (
        <div className="rows" >
            <div style={{marginTop: 30, marginRight: 50}}>
                <div>
                    <NavLink to='/'> Home </NavLink>
                </div>
                <div>
                    <NavLink to='/books/'> All books </NavLink>
                </div>
                <div>
                    <NavLink to='/authors/'> All authors </NavLink>
                </div>
                <div>
                    <NavLink to='/game_type/'> All Games </NavLink>
                </div>
                <form onSubmit={this.onFormSubmit} className="input-group">
                    <input
                        placeholder="Search...."
                        className="form-control"
                        value={this.state.term}
                        onChange={this.onInputChange}
                    />
                    <span className="input-group-btn">
                        <button type="submit" className="btn btn-secondary"> 
                            Search 
                        </button>
                    </span>
                </form>
                {
                    this.props.isAuthenticated ?
                    
                    <div>
                        <NavLink to = '/' onClick={()=>{this.props.logout()}}> Logout </NavLink>
                    </div>
                    :
                    <div> 
                        <NavLink to='/login/'> Login </NavLink> 
                    </div>
                }
            </div>
            
            <div style={{marginLeft: 30, marginTop: 0}}>
              <h1> Searched games </h1>
              {
                games.map(item => {
                    return (
                        <div key={item.name}>
                          <NavLink to = '/game_detail' onClick={()=>{this.props.game_detail(item)}}> {item.name} </NavLink>
                          <br/>
                        </div>
                      )
                })
              }
              {
                  games.length == 0 ?
                  <div>
                    No games matching your search
                  </div>
                  :
                  <div> 
                      
                  </div>
              }
            </div>
        </div>
      )
    }
}

const mapStateToProps = (state) => {
    return {
        token: state.general.term,
        isAuthenticated: state.auth.token !== null
    }
}
  
export default connect(mapStateToProps, { game_detail })(Game_Search);