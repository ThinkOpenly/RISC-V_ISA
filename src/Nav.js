import React, { Component } from "react";
import {
    Header,
    HeaderName,
    HeaderNavigation,
    HeaderMenuItem
} from "@carbon/react";

class Nav extends Component {
    /*
    constructor() {
        super();
    }
    */

    render() {
        const { isDarkMode, toggleDarkMode } = this.props;
        return (
            <div>
                <Header aria-label="RISC-V ISA">
                    <HeaderName href="#" prefix={"RISC-V"}>
                        ISA Reference
                    </HeaderName>
                    <HeaderNavigation aria-label="ISA">
                        <HeaderMenuItem>|</HeaderMenuItem>
                        <HeaderMenuItem href="https://riscv.org">RISC-V International</HeaderMenuItem>
                        <HeaderMenuItem href="https://riscv.org/technical/specifications/">RISC-V Specifications</HeaderMenuItem>
                        <HeaderMenuItem href="https://GitHub.com/riscv/sail-riscv">RISC-V Sail Model</HeaderMenuItem>
                        <HeaderMenuItem href="https://github.com/ThinkOpenly/sail/tree/json">RISC-V Sail to JSON</HeaderMenuItem>
                    </HeaderNavigation>
                    <button id="theme-switch" onClick={toggleDarkMode}>
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#5f6368"><path d="M480-120q-150 0-255-105T120-480q0-150 105-255t255-105q14 0 27.5 1t26.5 3q-41 29-65.5 75.5T444-660q0 90 63 153t153 63q55 0 101-24.5t75-65.5q2 13 3 26.5t1 27.5q0 150-105 255T480-120Z"/></svg>
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e8e8e8"><path d="M480-280q-83 0-141.5-58.5T280-480q0-83 58.5-141.5T480-680q83 0 141.5 58.5T680-480q0 83-58.5 141.5T480-280ZM200-440H40v-80h160v80Zm720 0H760v-80h160v80ZM440-760v-160h80v160h-80Zm0 720v-160h80v160h-80ZM256-650l-101-97 57-59 96 100-52 56Zm492 496-97-101 53-55 101 97-57 59Zm-98-550 97-101 59 57-100 96-56-52ZM154-212l101-97 55 53-97 101-59-57Z"/></svg>
                    </button>
                </Header>
            </div>
        );
    }
}

export default Nav;
