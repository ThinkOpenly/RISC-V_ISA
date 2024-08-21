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

var formats = [];

function genFormatList(tree,index,array) {
    formats.push(tree);
}

class App extends Component {

    constructor(props) {
        super(props);
        /* Is the constructor called twice?? */

        if (formats.length == 0)
            ISA.formats.forEach(genFormatList);
        this.state = {
            data: ISA.instructions,
            extensionSet: ISA.extensions,
            formatSet: formats,
            search: "",
            search_mnemonics: true,
            search_names: false,
        };
    }

    displayOperands(operands) {
        let all = "";
        let comma = "";
    
        for (let i = 0; i < operands.length; i++) {
            if (operands[i].optional) {
                all += comma + "[," + operands[i].name + "]";
            } else {
                all += comma + operands[i].name;
            }
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
            item.syntax;
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
        if(layout.field.startsWith("0b")){
            const binaryValue = layout.field.substring(2);
            const binaryDigits = binaryValue.split("");

            return binaryDigits.map((digit, index) => (
                <td className="instruction-field" key={key + "-" + index} colSpan={1}>{digit}</td>
            ));
        }
        else{
            return(<td className="instruction-field" key={key} colSpan={layout.size}>{layout.field}</td>);
        }
    }

    displayFields(layout) {
        let all = [];
        for (let i = 0; i < layout.length; i++) {
            all.push(this.displayField(layout[i],i));
        }
        return all;
    }

    displayBitScale(layout,width) {
        let all = [];
        for (let i = width-1; i >= 0; i--) {
            all.push(<td className="instruction-bit-number" key={i}>{("0" + i.toString()).slice(-2)}</td>);
        }
        return all;
    }

    displayLayoutRows(layout,width) {
        let all = [];
        let bits = 0;
        let start = 0;
        for (let i = 0; i < layout.length; i++) {
            bits += parseInt(layout[i].size);
            if (bits >= width) {
                all.push(<tr key={start}>{this.displayFields(layout.slice(start,i+1))}</tr>);
                start = i+1;
                bits = 0;
            }
        }
        return all;
    }

    displayLayout(layout) {
	let all = [];
        let width = 0;
        for (let i = 0; i < layout.length; i++) {
            width += parseInt(layout[i].size);
        }
        if (width > 32) width = 32;
        all.push(this.displayLayoutRows(layout,width));
        all.push(<tr key="bitScale">{this.displayBitScale(layout,width)}</tr>);
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
                                <td style={{textAlign: 'right'}}>{item.format}-type</td>
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
                        <td className="itemtitleext">{item.extensions.join()}</td>
                    </tr>
                </tbody>
            </table>
        );
    }

    matchEach(value) {
        return this.includes(value);
    }

    matchAny(extensions,extensionSet) {
        let id = document.getElementById("all-extensions");
        if (!id) return true; /* too early? */
        if (extensions.length == 0) return id.checked;
        if (extensions.length > 0 && extensionSet.length == 0) return false;
        for (let i = 0; i < extensions.length; i++) {
            if (extensionSet.includes(extensions[i])) return true;
        }
        return false;
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
                        if (this.state.formatSet.includes(data[i].format) &&
                            this.matchAny(data[i].extensions,this.state.extensionSet)) {
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

    genExtensionLabel(extension) {
        return (
            <table className="extensionlabel">
                <tbody>
                    <tr>
                        <td className="extensionversion">{extension}</td>
                    </tr>
                </tbody>
            </table>
        );
    }

    genExtensionCheckboxes(extensions) {
        let all = [];
        for (let i = 0; i < extensions.length; i++) {
            all.push(
                <Checkbox
                    defaultChecked
                    className="checkbox"
                    id={extensions[i]}
                    key={extensions[i]}
                    labelText={this.genExtensionLabel(extensions[i])}
                    disabled={false}
                    hideLabel={false}
                    onChange={(value, id, event) => {
                        this.filterByExtensions(id.checked, extensions[i]);
                    }}
                />
            );
        }
        return all;
    }

    genFormatCheckboxes(formats) {
        let all = [];
        for (let i = 0; i < formats.length; i++) {
            all.push(
                <Checkbox
                    defaultChecked
                    className="checkbox"
                    id={formats[i]}
                    key={formats[i]}
                    labelText={formats[i]}
                    disabled={false}
                    hideLabel={false}
                    onChange={(value, id, event) => {
                        this.filterByFormats(id.checked, formats[i]);
                    }}
                />
            );
        }
        return all;
    }

    search() {
        let id = document.getElementById("search-1");
        this.setState({ search: id.value.toLowerCase() });
    }

    filterAllExtensions(set) {
        let newSet = [];
        if (set) {
            newSet = ISA.extensions;
        }
        for (let i = 0; i < ISA.extensions.length; i++) {
            let id = document.getElementById(ISA.extensions[i]);
            id.checked = set;
        }
        this.setState({ extensionSet: newSet });
    }

    filterAllFormats(set) {
        let newSet = [];
        if (set) {
            newSet = formats;
        }
        for (let i = 0; i < formats.length; i++) {
            let id = document.getElementById(formats[i]);
            id.checked = set;
        }
        this.setState({ formatSet: newSet });
    }

    filterByExtensions(set, b) {
        let newSet = [];
        if (set) {
            newSet = this.state.extensionSet;
            newSet.push(b);
        } else {
            for (let i = 0; i < this.state.extensionSet.length; i++) {
                if (this.state.extensionSet[i] === b) continue;
                newSet.push(this.state.extensionSet[i]);
            }
        }
        this.setState({ extensionSet: newSet });
    }

    filterByFormats(set, b) {
        let newSet = [];
        if (set) {
            newSet = this.state.formatSet;
            newSet.push(b);
        } else {
            for (let i = 0; i < this.state.formatSet.length; i++) {
                if (this.state.formatSet[i] === b) continue;
                newSet.push(this.state.formatSet[i]);
            }
        }
        this.setState({ formatSet: newSet });
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
                            <div className="filterContainer">
                                <Accordion>
                                    <AccordionItem
                                        title="Extensions"
                                    >
                                        <fieldset className="checkboxes">
                                            <Checkbox
                                                defaultChecked
                                                className="checkbox"
                                                id="all-extensions"
                                                labelText="[all]"
                                                disabled={false}
                                                hideLabel={false}
                                                onChange={(value, id, event) => {
                                                    this.filterAllExtensions(id.checked);
                                                }}
                                            />
                                            {this.genExtensionCheckboxes(ISA.extensions)}
                                        </fieldset>
                                    </AccordionItem>
                                </Accordion>
                                <Accordion>
                                    <AccordionItem
                                        title="Instruction formats"
                                    >
                                        <fieldset className="checkboxes">
                                            <Checkbox
                                                defaultChecked
                                                className="checkbox"
                                                id="all-forms"
                                                labelText="[all]"
                                                disabled={false}
                                                hideLabel={false}
                                                onChange={(value, id, event) => {
                                                    this.filterAllFormats(id.checked);
                                                }}
                                            />
                                            {this.genFormatCheckboxes(ISA.formats)}
                                        </fieldset>
                                    </AccordionItem>
                                </Accordion>
                            </div>
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
