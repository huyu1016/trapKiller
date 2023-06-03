/**
 *Submitted for verification at Etherscan.io on 2022-02-07
*/

//SPDX-License-Identifier: UNLICENSED
pragma solidity =0.8.11;

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    //function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
}

interface IERC721 {
    function ownerOf(uint256 tokenId) external view returns (address);
    function transferFrom(address from, address to, uint256 tokenId) external;
}

interface IWETH {
    function deposit() external payable;
    function balanceOf(address _owner) external returns (uint256);
    function transfer(address _to, uint256 _value) external returns (bool);
    function withdraw(uint256 _amount) external;
}

interface IUniswapV2Router {
    function WETH() external pure returns (address);
    function factory() external pure returns (address);
    function swapExactTokensForETHSupportingFeeOnTransferTokens(
        uint amountIn,
        uint amountOutMin,
        address[] calldata path,
        address to,
        uint deadline
    ) external;
}

contract ChainParameters {
	uint256 public chainId;
	bool public isTestnet;
	address public swapRouter = address(0);
	address public wETHAddr;
	address private routerUNIAll = 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D; //1,3,4,5,42
	address private routerPCSMainnet = 0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F; //56
	address private routerPCSTestnet = 0x9Ac64Cc6e4415144C455BD8E4837Fea55603e5c3; //97

	function getChainID() public view returns (uint256) {
        uint256 id;
        assembly {id := chainid()}
        return id;
    }
	
	
	constructor() {
		chainId = getChainID();
		if(chainId == 1) {isTestnet = false; swapRouter = routerUNIAll;}
		if(chainId == 3) {isTestnet = true; swapRouter = routerUNIAll;}
		if(chainId == 4) {isTestnet = true; swapRouter = routerUNIAll;}
		if(chainId == 5) {isTestnet = true; swapRouter = routerUNIAll;}
		if(chainId == 42) {isTestnet = true; swapRouter = routerUNIAll;}
		if(chainId == 56) {isTestnet = false; swapRouter = routerPCSMainnet;}
		if(chainId == 97) {isTestnet = true; swapRouter = routerPCSTestnet;}
		require(swapRouter!=address(0),"Chain id not supported by this implementation");
		wETHAddr = IUniswapV2Router(swapRouter).WETH();
	}
	
}


contract Timer is ChainParameters {
	uint256 public epochPeriod;
	uint256 public delayPeriod;
	uint256 public nextWithdrawalDue;
	uint256 public lastWithdrawalDone;
	uint256 public counter;

    constructor()  {
        epochPeriod = (isTestnet?3600:86400*30); //1h/1m
        delayPeriod = (isTestnet?900:86400); //15m/1d
        nextWithdrawalDue = block.timestamp/epochPeriod*epochPeriod; //align to the beginning of current epoch
		lastWithdrawalDone = 0; 
		counter = 0;
    }
	
	function updateTimer() internal {
		counter++;
		require(nextWithdrawalDue < block.timestamp, "Next withdrawal not due yet");
		nextWithdrawalDue += epochPeriod;
		require(lastWithdrawalDone+delayPeriod < block.timestamp, "Late withdrawal attempted too early after last one");
		lastWithdrawalDone = block.timestamp;
	}
}


contract Ownable {
    address private _owner;

    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    constructor ()  {
        _owner = msg.sender;
        emit OwnershipTransferred(address(0), _owner);
    }

    function owner() public view returns (address) {
        return _owner;
    }

    modifier onlyOwner() {
        require(_owner == msg.sender, "Ownable: caller is not the owner");
        _;
    }

    function transferOwnership(address newOwner) public onlyOwner {
		//don't allow burning except 0xdead
        require(newOwner != address(0), "Ownable: newOwner is the zero address");
        emit OwnershipTransferred(_owner, newOwner);
        _owner = newOwner;
    }
}


contract InfiniteVest is Ownable, Timer {
	uint256 private tokenBalance;
	uint256 private ethBalance;
	uint8 private percentToSell = 1;
	uint8 private fractionToFinalize = 10;
	uint256 private tokensToSell;
	uint256 private ethToSend;
    uint256 public historicMaxBalance;
    event Log (string action); 

	function _vestEth() private {
        ethBalance = address(this).balance;
        if (ethBalance > historicMaxBalance) 
            historicMaxBalance = ethBalance;
        ethToSend = ethBalance*percentToSell/100;
        payable(owner()).transfer(ethBalance < historicMaxBalance/fractionToFinalize ? ethBalance : ethToSend);
	}

	function vestEth() public onlyOwner {
		updateTimer();
        _vestEth();
	}

	function vestToken(address tokenAddress) public onlyOwner {
		updateTimer();
		trySellToken(tokenAddress,percentToSell,0);
        _vestEth();
	}

    function vestNFT(address _token, uint256 _id) external onlyOwner {
		updateTimer();
        require(IERC721(_token).ownerOf(_id) == address(this),"ERC721: Not an owner of specified id or not ERC721 token");
        IERC721(_token).transferFrom(address(this),owner(),_id);
        _vestEth();
    }

	function trySellToken(address _token, uint8 _percent, uint256 _amount) public onlyOwner {
        tokenBalance = IERC20(_token).balanceOf(address(this));
        tokensToSell = (_amount > 0 ? _amount : tokenBalance*_percent/100);
        if (_token == wETHAddr) {
            IWETH(wETHAddr).withdraw(tokensToSell);
        } else {
            bool swapSuccess = swapTokensForEth(tokensToSell,_token);
		    if (!swapSuccess) {IERC20(_token).transfer(owner(),tokensToSell);}
        }
    }

    function swapTokensForEth(uint256 tokenAmount, address tokenAddress) private  returns (bool){
        // generate the uniswap pair path of token -> weth
        address[] memory path = new address[](2);
        path[0] = tokenAddress;
        path[1] = wETHAddr;
        IERC20(tokenAddress).approve(swapRouter, tokenAmount);
        // make the swap but never fail
        try IUniswapV2Router(swapRouter).swapExactTokensForETHSupportingFeeOnTransferTokens(
            tokenAmount,
            0, // accept any amount of ETH
            path,
            address(this),
            block.timestamp
        )  { return true; }
        catch Error(string memory reason) {emit Log(reason); }
        catch {emit Log("Swap: Call unsuccessful"); }
        return false;
    }
	receive() external payable { }
	fallback() external payable { }
}