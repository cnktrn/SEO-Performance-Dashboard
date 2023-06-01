import React from "react";
import {BrowserRouter, Link, Route, Switch} from "react-router-dom";
import SignUp from "./components/Authentication/SignUp.jsx";
import Login from "./components/Authentication/Login.jsx";
import './App.css';
import logo from './resources/MMLogo.png';

const App = () => {
    return (
        <BrowserRouter>
            <header className="header-bar">
                <img src={logo} alt="Logo" className="logo" />
            </header>
            <div className="login-screen">
                <h1>LMUxMM SEO Dashboard</h1>
                <div className="button-container">
                    <Link to="/login" className="login-button">Login</Link>
                    <Link to="/signup" className="signup-button">Sign Up</Link>
                </div>
                <Switch>
                    <Route path="/login" exact component={Login} />
                    <Route path="/signup" exact component={SignUp} />
                </Switch>
            </div>
        </BrowserRouter>
    )
}

export default App;
