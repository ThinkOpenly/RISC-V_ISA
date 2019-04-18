import React, { Component } from "react";
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

    genData = data => {
        let allJson = [];
        for (let i = 0; i < data.length; i++) {
            allJson.push(<p>{data[i].description}</p>);
        }
        return allJson;
    };
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
                    <br />
                    <br />
                    {this.genData(this.state.data)}
                </div>
            </div>
        );
    }
}

export default App;
