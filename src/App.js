import React, { Component } from "react";
import logo from "./logo.svg";
import "./App.scss";
import Nav from "./Nav";
import data from "./ISA.json";
import { TextInput } from "carbon-components";

class App extends Component {
    constructor() {
        super();
        this.state = {
            data: data
        };
    }
    render() {
        return (
            <div className="App">
                <div
                    data-floating-menu-container="true"
                    role="main"
                    className="pageContainer"
                >
                    <div className="homeContainer">
                        <Nav />
                        <h1>ISA</h1>
                    </div>
                </div>
            </div>
        );
    }
}

export default App;
