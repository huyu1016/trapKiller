pragma solidity 0.4.25;
contract TS{
    uint base = 1 ether;
    constructor() public {} 
    function TrickySend() public payable {
        msg.sender.send(base);
        base = 0;
    }
}