pragma solidity 0.4.25;
contract TS1{
    uint base = 1 ether;
    constructor() public {} 
    function TrickySend() public payable {
        msg.sender.transfer(base);
        base = 0;
    }
}