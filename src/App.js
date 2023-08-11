import React, { Component } from "react";
import "./App.scss";
import Nav from "./Nav";
import ISA from "./ISA.json";
import emnems from "./emnem.json";
import {
    Accordion,
    AccordionItem,
    Search,
    Checkbox,
    CodeSnippet,
    Link,
    StructuredListWrapper, StructuredListHead, StructuredListBody, StructuredListRow, StructuredListCell,
    DataTable, TableContainer, Table, TableHead, TableRow, TableHeader, TableBody, TableCell
} from "@carbon/react";
import { CopyToClipboard } from "react-copy-to-clipboard";

class App extends Component {

    constructor(props) {
        super(props);
        /* Is the constructor called twice?? */
        this.state = {
            data: ISA.instructions,
            search: "",
            search_mnemonics: true,
            search_names: false,
        };
    }

    displayOperands(operands) {
        let all = "";
        let comma = "";
        for (let i = 0; i < operands.length; i++) {
            all += comma + operands[i].name;
            comma = ",";
        }
        return all;
    }

    displayMnemonic(item) {
        const spaces = "               ";

        let gap = spaces.length - item.mnemonic.length;
        if (gap < 2) gap = 2;
        let s =
            item.mnemonic +
            spaces.substr(0,gap) +
            this.displayOperands(item.operands);
        let conditions = "";
        try {
            if (item.conditions.length > 0) {
                conditions = "(";
                let comma = "";
                for (let c = 0; c < item.conditions.length; c++) {
                    conditions += comma + item.conditions[c].field + "=" + item.conditions[c].value;
                    comma = ", ";
                }
                conditions += ")";
            }
        } catch(err) {}
        let key = "mnemonics-table-" + item.mnemonic;
        return (
            <table key={key}>
                <tbody>
                    <tr>
                        <td>
                            <CopyToClipboard text={s}>
                                <CodeSnippet
                                    className="syntax"
                                    key="syntax"
                                    feedback="Copied to clipboard"
                                    copyButtonDescription="Copy"
                                    ariaLabel="mnemonic"
                                    type="inline"
                                >
                                    {s}
                                </CodeSnippet>
                            </CopyToClipboard>
                        </td>
                        <td>
                            <p className="conditions">{conditions}</p>
                        </td>
                    </tr>
                </tbody>
            </table>
        );
    }

    displayField(layout,key) {
        return(<td className="instruction-field" key={key} colSpan={layout.size}>{layout.field}</td>);
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
        for (let i = 31; i >= 0; i--) {
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
                    {this.displayMnemonic(item)}
                    <br />
                    <table style={{width: '100%'}}>
                        <tbody>
                            <tr>
                                <td>
                                    <table className="instruction-layout">
                                        <tbody>
                                            {this.displayLayout(item.fields)}
                                        </tbody>
                                    </table>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    <br />
                    <CopyToClipboard text={item.function}>
                        <CodeSnippet
                            className="pseudocode"
                            key="pseudocode"
                            type="multi"
                            feedback="Copied to clipboard"
                        >
                            <p className="inner">{item.function}</p>
                        </CodeSnippet>
                    </CopyToClipboard>
                    <br />
                    <div className="prose">
                        {item.description}
                    </div>
                </div>
            </div>
        );
    }

    genTitle(item) {
        return (
            <table className="item">
                <tbody>
                    <tr>
                        <td className="itemtitledesc">{item.name}</td>
                        <td className="itemtitlemnem">{item.mnemonic}</td>
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
            {
                    if (
                        (this.state.search_mnemonics &&
                         data[i].mnemonic.startsWith(this.state.search)) ||
                        (this.state.search_names &&
                         this.state.search.split(" ").every(this.matchEach,data[i].name.toLowerCase()))
                    ) {
                        {
                            allJson.push(
                                <AccordionItem
                                    title={this.genTitle(data[i])}
                                    key={data[i].mnemonic}
                                >
                                    {this.genItem(data[i])}
                                </AccordionItem>
                            );
                        }
                    }
            }
        }
        return allJson;
    };

    search() {
        let id = document.getElementById("search-1");
        this.setState({ search: id.value.toLowerCase() });
    }

    genMultiLine(row,string) {
        let all = [];
        try {
          string.split("\n").map ((line) => (
            all.push(line),
            all.push(<br/>)
          ))
        }
        catch (err) {}
        return all;
    }

    displayOps(ops, optionals) {
        let all = "";
        let comma = "";
        for (let i = 0; i < ops.length; i++) {
            let optional = ops[i].optional[0] - '0';
            if (optional <= optionals) {
                all += comma + ops[i].name;
                comma = ",";
            }
        }
        return all;
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
                            <div className="accordianContainer">
                                <div className="searchContainer">
                                    <table>
                                        <tbody>
                                            <tr>
                                                <td style={{width: '50%', justifyContent: 'center'}}>
                                                    <Search
                                                        className="some-class"
                                                        name=""
                                                        defaultValue=""
                                                        labelText="Search"
                                                        closeButtonLabelText=""
                                                        placeholder="Search"
                                                        onChange={() => {
                                                            this.search();
                                                        }}
                                                        id="search-1"
                                                    />
                                                </td>
                                                <td>
                                                    <Checkbox
                                                        defaultChecked
                                                        className="checkbox"
                                                        id="search-mnemonics"
                                                        labelText="mnemonics"
                                                        disabled={false}
                                                        hideLabel={false}
                                                        onChange={(value, id, event) => {
                                                            this.setState({ search_mnemonics: id.checked });
                                                        }}
                                                    />
                                                    <Checkbox
                                                        className="checkbox"
                                                        id="search-names"
                                                        labelText="names"
                                                        disabled={false}
                                                        hideLabel={false}
                                                        onChange={(value, id, event) => {
                                                            this.setState({ search_names: id.checked });
                                                        }}
                                                    />
                                                </td>
                                            </tr>
                                        </tbody>
                                    </table>
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
