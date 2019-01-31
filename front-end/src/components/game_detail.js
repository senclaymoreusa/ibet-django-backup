import React, { Component } from 'react';
import { connect } from 'react-redux';
import Navigation from "./navigation";

class Game_Detail extends Component {

    render() {
      return(
        <div className='rows'>
          <div>
            <Navigation />
          </div>
          <div>
            <h1> Game Details </h1>
            <div> <b>name:</b>    {this.props.game_detail.name} </div>
            <br/>
            <div> <b>category:</b>    {this.props.game_detail.category_id.name} </div>
            <br/>
            <div> <b>start_time:</b>  {this.props.game_detail.start_time} </div>
            <br/>
            <div> <b>end_time:</b>    {this.props.game_detail.end_time} </div>
            <br/>
            <div> <b>opponent1:</b>   {this.props.game_detail.opponent1} </div>
            <br/>
            <div> <b>opponent2:</b>   {this.props.game_detail.opponent2} </div>
            <br/>
            <div> <b>description:</b> {this.props.game_detail.description} </div>
          </div>
        </div>
      )
    }
}

const mapStateToProps = (state) => {
    return {
        game_detail: state.general.game_detail
    }
}

export default connect(mapStateToProps)(Game_Detail);