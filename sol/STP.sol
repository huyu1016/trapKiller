pragma solidity ^0.4.25;

contract STP {

   address owner;
   uint value;

   constructor() public {
       owner = msg.sender;
   }

   modifier onlyOwner() {
       require(msg.sender == owner);
        _;
   }

   function withDrawEtherByOwner(address addr, uint amount) public payable onlyOwner
   {

       if(address(this).balance > amount)
        addr.transfer(amount);
   }

}