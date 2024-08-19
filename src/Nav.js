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
        return (
            <div>
                <Header aria-label="RISC-V ISA">
                    <HeaderName prefix={"RISC-V"}>
                        ISA Reference
                    </HeaderName>
                    <HeaderNavigation aria-label="ISA">
                        <span>|</span>
                        <HeaderMenuItem href="https://riscv.org">RISC-V International</HeaderMenuItem>
                        <HeaderMenuItem href="https://riscv.org/technical/specifications/">RISC-V Specifications</HeaderMenuItem>
                        <HeaderMenuItem href="https://GitHub.com/riscv/sail-riscv">RISC-V Sail Model</HeaderMenuItem>
                        <HeaderMenuItem href="https://GitHub.com/ThinkOpenly/riscvdecode">RISC-V Sail to JSON</HeaderMenuItem>
                    </HeaderNavigation>
                </Header>
            </div>
        );
    }
}

export default Nav;
