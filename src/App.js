import React, { Component } from "react";
import "./App.scss";
import Nav from "./Nav";
import data from "./ISA.json";
import { Accordion, AccordionItem, Search } from "carbon-components-react";

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
            console.log(data[i]);
            allJson.push(
                <AccordionItem
                    title={data[i].description}
                    onClick={e => {
                        console.log("click");
                    }}
                    onHeadingClick={e => {
                        console.log("heading click");
                    }}
                >
                    <div className="expandContainer">
                        <div className="column">
                            <h4>Form: </h4>
                            {data[i].form}
                        </div>
                    </div>
                </AccordionItem>
            );
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
                        <div className="mainContainer">
                            <div className="filterContainer">
                                <h3>Filter stuff here</h3>
                            </div>
                            <div className="accordianContainer">
                                <div className="searchContainer">
                                    <Search
                                        className="some-class"
                                        name=""
                                        defaultValue=""
                                        labelText="Search"
                                        closeButtonLabelText=""
                                        placeHolderText="Search"
                                        onChange={() => {
                                            console.log("searching");
                                        }}
                                        id="search-1"
                                    />
                                </div>
                                <Accordion>
                                    {this.genData(this.state.data)}
                                </Accordion>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
}

export default App;
