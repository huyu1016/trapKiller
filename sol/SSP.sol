pragma solidity ^0.8.17;

contract Trap {

    address owner;
    uint value;

    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }

    constructor() public {
        owner = msg.sender;
    }


    //SSP
    function changeInterest(uint newValue) public onlyOwner {
        value = newValue;
    }
}

