import React from "react";
import { Route } from "react-router-dom";
import Home from "./components/home";
import Books from "./components/books";
import Authors from "./components/authors";
import Game_Type from "./components/game_type";
import Game_List from "./components/game_list";
import Login from './components/login';
import Signup from './components/signup';
import Game_Detail from './components/game_detail';
import Game_Search from './components/game_search';

const BaseRouter = () => (
  <div>
    <Route exact path="/" component={Home} />
    <Route exact path="/books" component={Books} />
    <Route exact path="/authors" component={Authors} />
    <Route exact path="/game_type" component={Game_Type} />
    <Route exact path="/game_list" component={Game_List} />
    <Route exact path="/login" component={Login} />
    <Route exact path="/signup" component={Signup} />
    <Route exact path="/game_detail" component={Game_Detail} />
    <Route exact path="/game_search" component={Game_Search} />
  </div>
);

export default BaseRouter;