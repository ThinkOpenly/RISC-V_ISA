import React, { Component } from "react";
import "./App.css";
import Nav from "./Nav";
import ISA from "./ISA.json";
import {
    Accordion,
    AccordionItem,
    Search,
    Checkbox,
    CodeSnippet
} from "carbon-components-react";

const releases = [
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
    "v3.0B",
    "v3.1"
];

const cores = [
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
    "",
    "POWER9",
    "POWER10"
];

var classes = [];
var forms = [];

function genClassList(tree,index,array) {
    classes.push(tree.name);
    tree.chapters.forEach(genClassList);
}

function genFormList(tree,index,array) {
    forms.push(tree);
}

class App extends Component {

    constructor(props) {
        super(props);
        ISA.chapters.forEach(genClassList);
        ISA.forms.forEach(genFormList);
        this.state = {
            data: ISA.instructions,
            releaseSet: releases,
            classSet: classes,
            formSet: forms,
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
        let s = "";
        let newline = "";
        const spaces = "            ";

        for (let i = 0; i < item.mnemonics.length; i++) {
            let gap = spaces.length - item.mnemonics[i].mnemonic.length;
            if (gap < 2) gap = 2;
            s += newline +
                item.mnemonics[i].mnemonic +
                spaces.substr(0,gap) +
                this.displayRegs(item.mnemonics[i].regs);
            newline = "\n\r";
        }
        return s;
    }

    displayCode(item) {
        let s = "";
        let newline = "";
        for (let i = 0; i < item.code.length; i++) {
            s += newline + item.code[i];
            newline = "\n";
        }
        return s;
    }

    displayBody(item) {
        let all = [];
        for (let i = 0; i < item.body.length; i++) {
            all.push(<p key={i}>{item.body[i]}</p>);
        }
        return all;
    }

    displayField(layout,key) {
        let all = [];
        var d = layout.name;
        if (d.includes("opcode")) {
            d = d.replace("opcode",layout.value);
        }
        all.push(<td className="instruction-field" key={key} colSpan={layout.size}>{d}</td>);
        return all;
    }

    displayFields(layout) {
        let all = [];
        for (let i = 0; i < layout.length; i++) {
            all.push(this.displayField(layout[i],i));
        }
        return all;
    }

    displayBitScale(layout) {
        let all = [];
        for (let i = 0; i < 32; i++) {
            all.push(<td className="instruction-bit-number" key={i}>{("0" + i.toString()).slice(-2)}</td>);
        }
        return all;
    }

    displayLayoutRows(layout) {
        let all = [];
        let bits = 0;
        let start = 0;
        for (let i = 0; i < layout.length; i++) {
            bits += parseInt(layout[i].size);
            if (bits >= 32) {
                all.push(<tr key={start}>{this.displayFields(layout.slice(start,i+1))}</tr>);
                start = i+1;
                bits = 0;
            }
        }
        return all;
    }

    displayLayout(layout) {
	let all = [];
        all.push(this.displayLayoutRows(layout));
        all.push(<tr key="bitScale">{this.displayBitScale(layout)}</tr>);
        return (all);
    }

    genItem(item) {
        return (
            <div className="expandContainer">
                <div className="column">
                    <CodeSnippet
                        className="syntax"
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
                    <br />
                    <table style={{width: '100%'}}>
                        <tbody>
                            <tr>
                                <td>
                                    <table className="instruction-layout">
                                        <tbody>
                                            {this.displayLayout(item.layout)}
                                        </tbody>
                                    </table>
                                </td>
                                <td style={{textAlign: 'right'}}>{item.form}</td>
                            </tr>
                        </tbody>
                    </table>
                    <br />
                    <CodeSnippet
                        className="pseudocode"
                        type="multi"
                        feedback="Copied to clipboard"
                        onClick={() => {
                            console.log("clicked");
                        }}
                    >
                        {this.displayCode(item)}
                    </CodeSnippet>
                    <br />
                    <div className="prose">
                        {this.displayBody(item)}
                    </div>
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

    matchEach(value) {
        return this.includes(value);
    }

    genData = data => {
        let allJson = [];
        for (let i = 0; i < data.length; i++) {
            for (let m = 0; m < data[i].mnemonics.length; m++) {
                if (
                    data[i].mnemonics[m].mnemonic.startsWith(this.state.search) ||
                    this.state.search.split(" ").every(this.matchEach,data[i].description.toLowerCase())
                ) {
                    if (
                        this.state.releaseSet.includes(
                            data[i].mnemonics[m].release
                        ) &&
                        this.state.classSet.includes(
                            data[i].category
                        ) &&
                        this.state.formSet.includes(
                            data[i].form
                        )
                    ) {
                        allJson.push(
                            <AccordionItem
                                title={this.genTitle(data[i])}
                                key={data[i].mnemonics[0].mnemonic}
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
                        <td className="releaseversion">{releases[i]}</td>
                        <td className="releasecore">{cores[i]}</td>
                    </tr>
                </tbody>
            </table>
        );
    }

    genReleaseCheckboxes() {
        let all = [];
        for (let i = 0; i < releases.length; i++) {
            all.push(
                <Checkbox
                    defaultChecked
                    className="checkbox"
                    id={releases[i]}
                    key={releases[i]}
                    labelText={this.genReleaseLabel(i)}
                    disabled={false}
                    hideLabel={false}
                    wrapperClassName=""
                    onChange={e => {
                        this.filterByReleases(e, releases[i]);
                    }}
                />
            );
        }
        return all;
    }

    genClassCheckboxes(chapters) {
        let all = [];
        for (let i = 0; i < chapters.length; i++) {
            all.push(
                <Checkbox
                    defaultChecked
                    className="checkbox"
                    id={chapters[i].name}
                    key={chapters[i].name}
                    labelText={chapters[i].name}
                    disabled={false}
                    hideLabel={false}
                    wrapperClassName=""
                    onChange={e => {
                        this.filterByClasses(e, chapters[i].name);
                    }}
                />
            );
        }
        return all;
    }

    genFormCheckboxes(forms) {
        let all = [];
        for (let i = 0; i < forms.length; i++) {
            all.push(
                <Checkbox
                    defaultChecked
                    className="checkbox"
                    id={forms[i]}
                    key={forms[i]}
                    labelText={forms[i]}
                    disabled={false}
                    hideLabel={false}
                    wrapperClassName=""
                    onChange={e => {
                        this.filterByForms(e, forms[i]);
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

    filterAllReleases(set) {
        let newSet = [];
        if (set) {
            newSet = releases;
        }
        for (let i = 0; i < releases.length; i++) {
            let id = document.getElementById(releases[i]);
            id.checked = set;
        }
        this.setState({ releaseSet: newSet });
    }

    filterAllClasses(set) {
        let newSet = [];
        if (set) {
            newSet = classes;
        }
        for (let i = 0; i < classes.length; i++) {
            let id = document.getElementById(classes[i]);
            id.checked = set;
        }
        this.setState({ classSet: newSet });
    }

    filterAllForms(set) {
        let newSet = [];
        if (set) {
            newSet = forms;
        }
        for (let i = 0; i < forms.length; i++) {
            let id = document.getElementById(forms[i]);
            id.checked = set;
        }
        this.setState({ formSet: newSet });
    }

    filterByReleases(set, b) {
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

    filterByClasses(set, b) {
        let newSet = [];
        if (set) {
            newSet = this.state.classSet;
            newSet.push(b);
        } else {
            for (let i = 0; i < this.state.classSet.length; i++) {
                if (this.state.classSet[i] === b) continue;
                newSet.push(this.state.classSet[i]);
            }
        }
        this.setState({ classSet: newSet });
    }

    filterByForms(set, b) {
        let newSet = [];
        if (set) {
            newSet = this.state.formSet;
            newSet.push(b);
        } else {
            for (let i = 0; i < this.state.formSet.length; i++) {
                if (this.state.formSet[i] === b) continue;
                newSet.push(this.state.formSet[i]);
            }
        }
        this.setState({ formSet: newSet });
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
                                <Accordion>
                                    <AccordionItem
                                        title="ISA levels"
                                    >
                                        <fieldset className="checkboxes">
                                            <Checkbox
                                                defaultChecked
                                                className="checkbox"
                                                id="all-releases"
                                                labelText="[all]"
                                                disabled={false}
                                                hideLabel={false}
                                                wrapperClassName=""
                                                onChange={e => {
                                                    this.filterAllReleases(e);
                                                }}
                                            />
                                            {this.genReleaseCheckboxes()}
                                        </fieldset>
                                    </AccordionItem>
                                </Accordion>
                                <Accordion>
                                    <AccordionItem
                                        title="Instruction classes"
                                    >
                                        <fieldset className="checkboxes">
                                            <Checkbox
                                                defaultChecked
                                                className="checkbox"
                                                id="all-classes"
                                                labelText="[all]"
                                                disabled={false}
                                                hideLabel={false}
                                                wrapperClassName=""
                                                onChange={e => {
                                                    this.filterAllClasses(e);
                                                }}
                                            />
                                            {this.genClassCheckboxes(ISA.chapters)}
                                        </fieldset>
                                    </AccordionItem>
                                </Accordion>
                                <Accordion>
                                    <AccordionItem
                                        title="Instruction forms"
                                    >
                                        <fieldset className="checkboxes">
                                            <Checkbox
                                                defaultChecked
                                                className="checkbox"
                                                id="all-forms"
                                                labelText="[all]"
                                                disabled={false}
                                                hideLabel={false}
                                                wrapperClassName=""
                                                onChange={e => {
                                                    this.filterAllForms(e);
                                                }}
                                            />
                                            {this.genFormCheckboxes(ISA.forms)}
                                        </fieldset>
                                    </AccordionItem>
                                </Accordion>
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
