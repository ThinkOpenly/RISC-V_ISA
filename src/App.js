import React, { Component } from "react";
import "./App.scss";
import Nav from "./Nav";
import data from "./ISA.json";
import {
    Accordion,
    AccordionItem,
    Search,
    Checkbox,
    CodeSnippet
} from "carbon-components-react";

class App extends Component {
    releases = [
        "P1",
        "P2",
        "PPC",
        "v2.00",
        "v2.01",
        "v2.02",
        "v2.03",
        "v2.04",
        "v2.05",
        "v2.06",
        "v2.07",
        "v3.0",
        "v3.0B"
    ];
    cores = [
        "POWER1",
        "POWER2",
        "PPC970",
        "POWER4",
        "POWER4+",
        "POWER5",
        "",
        "POWER5+",
        "POWER6",
        "POWER7",
        "POWER8",
        "POWER9",
        "future"
    ];

    constructor() {
        super();
        this.state = {
            data: data,
            releaseSet: this.releases,
            search: ""
        };
    }

    displayRegs(regs) {
        let all = "";
        for (let i = 0; i < regs.length; i++) {
            all += regs[i] + ", ";
        }
        return all.substring(0, all.length - 2);
    }

    displayMnemonics(item) {
        let all = [];
        let newline = "";
        const spaces = "            ";

        for (let i = 0; i < item.mnemonics.length; i++) {
            let gap = spaces.length - item.mnemonics[i].mnemonic.length;
            if (gap < 2) gap = 2;
            all.push(
                newline +
                item.mnemonics[i].mnemonic +
                spaces.substr(0,gap) +
                this.displayRegs(item.mnemonics[i].regs)
            );
            newline = "\n\r";
        }
        return all;
    }

    displayCode(item) {
        let all = [];
        for (let i = 0; i < item.code.length; i++) {
            all.push(item.code[i] + "\n");
        }
        return all;
    }

    displayBody(item) {
        let all = [];
        for (let i = 0; i < item.body.length; i++) {
            all.push(<p>{item.body[i]}</p>);
        }
        return all;
    }

    genItem(item) {
        return (
            <div className="expandContainer">
                <div className="column">
                    <CodeSnippet
                        className="pseudocode"
                        feedback="Copied to clipboard"
                        copyButtonDescription="Copy"
                        ariaLabel="mnemonic"
                        onClick={() => {
                            console.log("clicked");
                        }}
                        type="multi"
                    >
                        {this.displayMnemonics(item)}
                    </CodeSnippet>
                    <h4>Pseudocode:</h4>
                    <CodeSnippet
                        type="multi"
                        feedback="Copied to clipboard"
                        onClick={() => {
                            console.log("clicked");
                        }}
                    >
                        {this.displayCode(item)}
                    </CodeSnippet>
                    <br />
                    <br />
                    {this.displayBody(item)}
                </div>
            </div>
        );
    }

    genTitle(item) {
        let s = "";
        let comma = "";
        for (let i = 0; i < item.mnemonics.length; i++) {
            s = s + comma + item.mnemonics[i].mnemonic;
            comma = ", ";
        }
        return (
            <table className="item">
                <tbody>
                    <tr>
                        <td className="itemtitledesc">{item.description}</td>
                        <td className="itemtitlemnem">{s}</td>
                    </tr>
                </tbody>
            </table>
        );
    }

    genData = data => {
        let allJson = [];
        for (let i = 0; i < data.length; i++) {
            for (let m = 0; m < data[i].mnemonics.length; m++) {
                if (
                    data[i].mnemonics[m].mnemonic.startsWith(this.state.search)
                ) {
                    if (
                        this.state.releaseSet.includes(
                            data[i].mnemonics[m].release
                        )
                    ) {
                        allJson.push(
                            <AccordionItem
                                title={this.genTitle(data[i])}
                                onClick={e => {
                                    console.log("click");
                                }}
                                onHeadingClick={e => {
                                    console.log("heading click");
                                }}
                            >
                                {this.genItem(data[i])}
                            </AccordionItem>
                        );
                        break;
                    }
                }
            }
        }
        return allJson;
    };

    genReleaseLabel(i) {
        return (
            <table className="releaselabel">
                <tbody>
                    <tr>
                        <td className="releaseversion">{this.releases[i]}</td>
                        <td className="releasecore">{this.cores[i]}</td>
                    </tr>
                </tbody>
            </table>
        );
    }

    genReleaseCheckboxes() {
        let all = [];
        for (let i = 0; i < this.releases.length; i++) {
            all.push(
                <Checkbox
                    defaultChecked
                    className="checkbox"
                    id={this.releases[i]}
                    labelText={this.genReleaseLabel(i)}
                    disabled={false}
                    hideLabel={false}
                    wrapperClassName=""
                    onChange={e => {
                        this.filter(e, this.releases[i]);
                    }}
                />
            );
        }
        return all;
    }

    search() {
        let id = document.getElementById("search-1");
        this.setState({ search: id.value });
    }

    filterAll(set) {
        let newSet = [];
        if (set) {
            newSet = this.releases;
        }
        for (let i = 0; i < this.releases.length; i++) {
            let id = document.getElementById(this.releases[i]);
            id.checked = set;
        }
        this.setState({ releaseSet: newSet });
    }

    filter(set, b) {
        let newSet = [];
        if (set) {
            newSet = this.state.releaseSet;
            newSet.push(b);
        } else {
            for (let i = 0; i < this.state.releaseSet.length; i++) {
                if (this.state.releaseSet[i] === b) continue;
                newSet.push(this.state.releaseSet[i]);
            }
        }
        this.setState({ releaseSet: newSet });
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
                        <div className="mainContainer">
                            <div className="filterContainer">
                                <fieldset className="checkboxes">
                                    <legend className="filter-heading">
                                        Restrict results to ISA levels:
                                    </legend>
                                    <Checkbox
                                        defaultChecked
                                        className="checkbox"
                                        id="all-releases"
                                        labelText="[all]"
                                        disabled={false}
                                        hideLabel={false}
                                        wrapperClassName=""
                                        onChange={e => {
                                            this.filterAll(e);
                                        }}
                                    />
                                    {this.genReleaseCheckboxes()}
                                </fieldset>
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
                                            this.search();
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
