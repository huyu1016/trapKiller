pragma solidity ^0.4.25;

contract father {
     address owner;

     constructor() public {
       owner = msg.sender;
     }

     modifier onlyOwner() {
          require(msg.sender == owner);
          _;
     }
}

contract test is father{

   function withDrawEtherByOwner(address addr, uint amount) public payable onlyOwner 
   {
        addr.send(amount);

        if (amount > 1)
          addr.send(amount);

     if (amount > 1){
          addr.send(amount);
     }

     if (amount > 1){
          addr.send(amount);
     }else{
          addr.send(1);
     }


   }

}

contract test1 {

     function testfunc(uint amount) public returns(bool)
     {
        return true;
     }
}
