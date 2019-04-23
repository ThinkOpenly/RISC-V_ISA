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

    displayRegs(regs) {
        let all = []
        for (let i = 0; i < regs.length; i++) {
            all.push(
                <td>{regs[i]}</td>
            );
        }
        return(all);
    }

    displayMnemonics(item) {
        let all = [];
        for (let i = 0; i < item.mnemonics.length; i++) {
            all.push(
                <tr>
                <td>{item.mnemonics[i].mnemonic}</td>
                {this.displayRegs(item.mnemonics[i].regs)}
                </tr>
            );
        }
        return (all);
    }

    displayCode(item) {
        let all = [];
        for (let i = 0; i < item.code.length; i++) {
            all.push(
                <pre>
                {item.code[i]}
                </pre>
            );
        }
        return (all);
    }

    displayBody(item) {
        let all = [];
        for (let i = 0; i < item.body.length; i++) {
            all.push(
                <p>{item.body[i]}</p>
            );
        }
        return (all);
    }

    genItem(item) {
        return (
            <div className="expandContainer">
                    <div className="expandContainer">
                        <div className="column">
                            <h4>Mnemonics:</h4>
                            <table>
                            {this.displayMnemonics(item)}
                            </table>
                            <h4>Code:</h4>
                            {this.displayCode(item)}
                            {this.displayBody(item)}
                        </div>
                    </div>
            </div>
        );
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
                    {this.genItem(data[i])}
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
