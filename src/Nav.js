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
                <Header aria-label="PowerISA">
                    <HeaderName href="#" prefix={"Power"}>
                        ISA Reference
                    </HeaderName>
                    <HeaderNavigation aria-label="ISA">
                        <HeaderMenuItem>|</HeaderMenuItem>
                        <HeaderMenuItem href="https://www.IBM.com">IBM</HeaderMenuItem>
                        <HeaderMenuItem href="https://OpenPOWERFoundation.org">The OpenPOWER Foundation</HeaderMenuItem>
                        <HeaderMenuItem href="https://www.ibm.com/systems/power/openpower/">IBM Portal for OpenPOWER</HeaderMenuItem>
                        <HeaderMenuItem href="https://developer.ibm.com/linuxonpower/">Linux on IBM Power Developer Portal</HeaderMenuItem>
                    </HeaderNavigation>
                </Header>
            </div>
        );
    }
}

export default Nav;
