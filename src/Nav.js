import React, { Component } from "react";
import {
    Header,
    HeaderName,
    HeaderNavigation,
    HeaderMenuItem
} from "carbon-components-react/lib/components/UIShell";

class Nav extends Component {
    constructor() {
        super();
    }

    render() {
        return (
            <div>
                <Header>
                    <HeaderName href="#" prefix={"Power"}>
                        ISA
                    </HeaderName>
                    <HeaderNavigation aria-label="ISA">
                        <HeaderMenuItem href="#">Will</HeaderMenuItem>
                        <HeaderMenuItem href="#">We</HeaderMenuItem>
                        <HeaderMenuItem href="#">Navigate?</HeaderMenuItem>
                    </HeaderNavigation>
                </Header>
            </div>
        );
    }
}

export default Nav;
