import React from "react";
import { Route } from "react-router-dom";
import Home from "./components/home";
import Game_Type from "./components/game_type";
import Game_List from "./components/game_list";
import Login from './components/login';
import Signup from './components/signup';
import Game_Detail from './components/game_detail';
import Game_Search from './components/game_search';
import Profile from './components/profile';
import Update from './components/update_profile';
import Change_Email from './components/change_email'
import Forget_Password from './components/forget_password'
import Reset_Password from './components/reset_password'
import Email_Sent from './components/email_sent'
import Reset_Password_Done from './components/reset_password_done'
import Referral from './components/referral'
import Balance from './components/balance'
import Activation from './components/activation'
import Activate from './components/activate'

const BaseRouter = () => (
  <div>
    <Route exact path="/" component={Home} />
    <Route exact path="/game_type/" component={Game_Type} />
    <Route exact path="/game_list/:term?" component={Game_List} />
    <Route exact path="/login" component={Login} />
    <Route exact path="/signup/:filter?" component={Signup} />
    <Route exact path="/game_detail/:id?" component={Game_Detail} />
    <Route exact path="/game_search/:term?" component={Game_Search} />
    <Route exact path="/profile" component={Profile} />
    <Route exact path="/update_profile" component={Update} />
    <Route exact path="/change_email" component={Change_Email} />
    <Route exact path="/forget_password" component={Forget_Password} />
    <Route exact path="/reset_password/:filter?" component={Reset_Password} />
    <Route exact path="/email_sent" component={Email_Sent} />
    <Route exact path="/reset_password_done" component={Reset_Password_Done} />
    <Route exact path="/referral" component={Referral} />
    <Route exact path="/balance" component={Balance} />
    <Route exact path="/activation" component={Activation} />
    <Route exact path="/activate/:token?" component={Activate} />
  </div>
);

export default BaseRouter;