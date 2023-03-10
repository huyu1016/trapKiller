// SPDX-License-Identifier: MIT
pragma solidity ^0.4.25;

contract SP {
    address owner;

    constructor() public{
        owner = msg.sender;
    }

    modifier ownercontrol() {
        require (msg.sender == owner);
        _;
    }

    function kill(address addr) public ownercontrol{
        selfdestruct(addr);
    }
}
